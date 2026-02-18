import datetime as dt
import enum
import itertools
from collections.abc import Callable
from datetime import date
from enum import Enum
from typing import Annotated, Literal, Union

import pandas as pd
from cachetools import LFUCache, cached
from fastapi import APIRouter, Query
from pandas import Timestamp
from pydantic import BaseModel, Field

from exchange_calendar_service.core.common.context import Context
from exchange_calendar_service.core.common.util import get_enum_key_literal_type
from exchange_calendar_service.core.util import find_interval


@enum.unique
class Tags(str, Enum):
    SPECIAL_OPEN = "special open"
    SPECIAL_CLOSE = "special close"
    QUARTERLY_EXPIRY = "quarterly expiry"
    MONTHLY_EXPIRY = "monthly expiry"
    MONTH_END = "month end"
    HOLIDAY = "holiday"
    WEEKEND = "weekend"
    REGULAR = "regular"


class AbstractDay(BaseModel):
    date: dt.date
    name: str | None = None
    tags: set[Tags]


class Session(BaseModel):
    open: dt.time
    close: dt.time


class BusinessDay(AbstractDay):
    business_day: Literal[True] = True
    session: Session


class NonBusinessDay(AbstractDay):
    business_day: Literal[False] = False


Day = Annotated[Union[BusinessDay, NonBusinessDay], Field(discriminator="business_day")]


class ExchangeInfo(BaseModel):
    mic: str
    tz: str


class SeriesIterator:
    """A forward-only cursor over a pandas Series with peek/next semantics."""

    def __init__(self, series):
        self._it = iter(series.items())
        self._current = next(self._it, None)

    def is_empty(self):
        return self._current is None

    def peek(self):
        return self._current

    def next(self):
        value = self.peek()
        self._current = next(self._it, None)
        return value

    def advance(self, d: pd.Timestamp) -> tuple[pd.Timestamp, str] | None:
        while not self.is_empty() and self.peek()[0] < d:
            self.next()
        return self.peek() if not self.is_empty() and self.peek()[0] == d else None


def get_router(exchanges_enum: type[Enum]):
    # Collection of all supported MICs.
    MICS = tuple(sorted(exchanges_enum.__members__.keys()))

    # A string type that only allows supported MICs.
    SupportedMIC = get_enum_key_literal_type(exchanges_enum)

    # Type alias for a tuple that can only contain supported MICs, with examples.
    SupportedMICs = Annotated[tuple[SupportedMIC, ...], Field(examples=[MICS[:10]])]

    router = APIRouter()

    @router.get(
        "/exchanges",
        tags=["Reference"],
        summary="Get a list of supported exchange codes, i.e. MICs.",
        description="Returns the list of supported MICs.",
        operation_id="getExchanges",
        responses={200: {"description": "List of supported MICs."}},
    )
    async def get_exchanges() -> SupportedMICs:
        """
        Return the list of supported MICs.
        """
        return tuple(exchanges_enum.__members__.keys())

    @router.get(
        "/exchanges/{mic}",
        tags=["Reference"],
        summary="Get information about a single exchange.",
        description="Returns information about a single exchange.",
        operation_id="getExchangeInfo",
        responses={200: {"description": "Information about a single exchange."}},
    )
    async def get_exchange_info(mic: SupportedMIC) -> ExchangeInfo:
        """
        Return information about a single exchange.
        """
        c = Context().cache.get(mic)
        return ExchangeInfo(mic=mic, tz=str(c.tz))

    # Cache return values. Allow for two times the number of operating MICs.
    @cached(LFUCache(maxsize=2 * len(MICS)))
    def _get_days(
        mic: SupportedMIC,
        start: pd.Timestamp,
        end: pd.Timestamp,
        business_day: bool | None = None,
        include_tags: frozenset[Tags] | None = None,
        exclude_tags: frozenset[Tags] | None = None,
        limit: Annotated[int, Field(gt=0)] | None = None,
        order: Literal["asc", "desc"] = "asc",
    ) -> tuple[Day, ...]:
        """
        Core method to return days with the desired properties for a given MIC and date range.

        This method does most of the heavy lifting.

        Parameters
        ----------
        mic : SupportedMIC
            The MIC of the exchange.
        start : pd.Timestamp
            The start of the period (inclusive).
        end : pd.Timestamp
            The end of the period (inclusive).
        business_day : bool or None, optional
            If set, only include (non) business days.
        include_tags : frozenset of Tags or None, optional
            If set, only include days that have all of the given tags.
        exclude_tags : frozenset of Tags or None, optional
            If set, exclude days that have any of the given tags.
        limit : int or None, optional
            If set, limit the number of returned days.
        order : {'asc', 'desc'}, default 'asc'
            The sort order of the returned days by date.

        Returns
        -------
        tuple of Day
            The matching days for the given MIC and date range.
        """

        def is_included(tags: set[Tags], business_day0: bool) -> bool:
            if business_day is not None and business_day != business_day0:
                return False
            if include_tags is not None and not include_tags.issubset(tags):
                return False
            if exclude_tags and exclude_tags.intersection(tags):
                return False
            return True

        # Get exchange calendar for MIC.
        c = Context().cache.get(mic)

        # Matching days accumulated here.
        days: dict[dt.date, Day] = dict()

        # Chunk size for incremental search.
        CHUNK_SIZE_DAYS = 30

        if limit is None:
            # No limit: process entire range at once.
            _get_days0(business_day, c, days, end, is_included, start)
        else:
            # Process in chunks until limit is reached or range exhausted.
            if order == "asc":
                chunk_start = start
                while chunk_start <= end and len(days) < limit:
                    chunk_end = min(
                        chunk_start + pd.Timedelta(days=CHUNK_SIZE_DAYS - 1), end
                    )
                    _get_days0(
                        business_day, c, days, chunk_end, is_included, chunk_start
                    )
                    chunk_start = chunk_end + pd.Timedelta(days=1)
            else:  # order == "desc"
                chunk_end = end
                while chunk_end >= start and len(days) < limit:
                    chunk_start = max(
                        chunk_end - pd.Timedelta(days=CHUNK_SIZE_DAYS - 1), start
                    )
                    _get_days0(
                        business_day, c, days, chunk_end, is_included, chunk_start
                    )
                    chunk_end = chunk_start - pd.Timedelta(days=1)

        return tuple(
            days[d]
            for d in itertools.islice(sorted(days, reverse=order == "desc"), limit)
        )

    def _get_days0(
        business_day: bool | None,
        c,
        days: dict[date, BusinessDay | NonBusinessDay],
        end: Timestamp,
        is_included: Callable[..., bool],
        start: Timestamp,
    ):
        if business_day is None or not business_day:
            # Weekend days can only coincide with holidays, but no other special days.

            weekend_days = SeriesIterator(
                c.weekend_days.holidays(start=start, end=end, return_name=True)
            )

            holidays = SeriesIterator(
                c.holidays_all.holidays(start=start, end=end, return_name=True)
            )

            while not weekend_days.is_empty() or not holidays.is_empty():
                d: pd.Timestamp | None = None
                name: str | None = None
                tags: set[Tags] = set()

                d_weekend = weekend_days.peek()
                d_holiday = holidays.peek()

                if d_weekend:
                    if d_holiday:
                        if d_weekend[0] < d_holiday[0]:
                            d = d_weekend[0]
                            tags |= {Tags.WEEKEND}
                            weekend_days.next()
                        elif d_weekend[0] == d_holiday[0]:
                            d = d_weekend[0]
                            name = d_holiday[1]
                            tags |= {Tags.WEEKEND, Tags.HOLIDAY}
                            weekend_days.next()
                            holidays.next()
                        else:
                            d = d_holiday[0]
                            name = d_holiday[1]
                            tags |= {Tags.HOLIDAY}
                            holidays.next()
                    else:
                        d = d_weekend[0]
                        tags |= {Tags.WEEKEND}
                        weekend_days.next()
                else:
                    d = d_holiday[0]
                    name = d_holiday[1]
                    tags |= {Tags.HOLIDAY}
                    holidays.next()

                if is_included(tags, False):
                    days[d] = NonBusinessDay(
                        date=d.to_pydatetime().date(),
                        name=name,
                        tags=tags,
                    )

        if business_day is None or business_day:
            business_day_candidates = c.week_days.holidays(
                start=start, end=end, return_name=False
            )

            if (
                business_day_candidates is not None
                and not business_day_candidates.empty
            ):
                # Weekdays can coincide with holidays (which then makes them non-business days), but also other special
                # business days.
                holidays = SeriesIterator(
                    c.holidays_all.holidays(start=start, end=end, return_name=True)
                )
                special_closes = {
                    t: SeriesIterator(
                        cal.holidays(start=start, end=end, return_name=True)
                    )
                    for t, cal in c.special_closes
                }
                special_opens = {
                    t: SeriesIterator(
                        cal.holidays(start=start, end=end, return_name=True)
                    )
                    for t, cal in c.special_opens
                }
                quarterly_expiries = SeriesIterator(
                    c.quarterly_expiries.holidays(
                        start=start, end=end, return_name=True
                    )
                )
                monthly_expiries = SeriesIterator(
                    c.monthly_expiries.holidays(start=start, end=end, return_name=True)
                )
                ends_of_month = SeriesIterator(
                    c.last_trading_days_of_months.holidays(start, end, return_name=True)
                )

                for d in business_day_candidates:
                    name = None
                    tags = set()
                    holiday = holidays.advance(d)

                    if holiday:
                        name = holiday[1]
                        tags = {Tags.HOLIDAY}

                        if is_included(tags, False):
                            days[d] = NonBusinessDay(
                                date=d.to_pydatetime().date(),
                                name=name,
                                tags=tags,
                            )

                        continue

                    # Assume regular trading day for now.
                    tags |= {Tags.REGULAR}
                    session = Session(
                        open=find_interval(c.open_times0, d)[1],
                        close=find_interval(c.close_times0, d)[1],
                    )

                    for t, cal in special_opens.items():
                        special_open = cal.advance(d)
                        if special_open:
                            name = special_open[1]
                            tags -= {Tags.REGULAR}
                            tags |= {Tags.SPECIAL_OPEN}
                            session.open = t

                    for t, dates in c.special_opens_adhoc:
                        if d in dates:
                            tags -= {Tags.REGULAR}
                            tags |= {Tags.SPECIAL_OPEN}
                            session.open = t

                    for t, cal in special_closes.items():
                        special_close = cal.advance(d)
                        if special_close:
                            name = special_close[1]
                            tags -= {Tags.REGULAR}
                            tags |= {Tags.SPECIAL_CLOSE}
                            session.close = t

                    for t, dates in c.special_closes_adhoc:
                        if d in dates:
                            tags -= {Tags.REGULAR}
                            tags |= {Tags.SPECIAL_CLOSE}
                            session.close = t

                    quarterly_expiry = quarterly_expiries.advance(d)
                    if quarterly_expiry:
                        tags |= {Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY}

                    monthly_expiry = monthly_expiries.advance(d)
                    if monthly_expiry:
                        tags |= {Tags.MONTHLY_EXPIRY}

                    end_of_month = ends_of_month.advance(d)
                    if end_of_month:
                        tags |= {Tags.MONTH_END}

                    if is_included(tags, True):
                        days[d] = BusinessDay(
                            date=d.to_pydatetime().date(),
                            name=name,
                            session=session,
                            tags=tags,
                        )

    @router.get(
        "/exchanges/{mic}/days",
        tags=["Days"],
        summary="Get days in a date range that match criteria.",
        description=r"""For an  exchange, this endpoint returns the list of days in a given date range that match the given criteria.

Start and end date are mandatory and inclusive.

Filter criteria are optional:
- `business_day`: If set, only include (non) business days.
- `include_tags`: If set, only include days that have at least one of the given tags.
- `exclude_tags`: If set, exclude days that have any of the given tags.

Sorting and limiting are optional:
- `order`: The sort order of the returned days by date (default: ascending).
- `limit`: If set, limit the number of returned days.

Note: The `limit` parameter applies to the selected days in the order they are returned in. That is, if `order` is 
`asc`, the first `limit` days with the smallest dates are returned, and vice versa if `order` is `desc`. 
""",
        operation_id="listExchangeDays",
        responses={200: {"description": "List of days matching the criteria."}},
        response_model_exclude_none=True,
    )
    def list_exchange_days(
        mic: SupportedMIC,
        start: dt.date,
        end: dt.date,
        business_day: bool | None = None,
        include_tags: Annotated[list[Tags] | None, Query()] = None,
        exclude_tags: Annotated[list[Tags] | None, Query()] = None,
        order: Literal["asc", "desc"] = "asc",
        limit: Annotated[int, Field(gt=0)] | None = None,
    ) -> tuple[Day, ...]:
        """
        Describe the given day on the given exchange.

        Parameters
        ----------
        mic : SupportedMIC
            The MIC of the exchange.
        start : pd.Timestamp
            The start of the period (inclusive).
        end : pd.Timestamp
            The end of the period (inclusive).
        business_day : bool or None, optional
            If set, only include (non) business days.
        include_tags : frozenset of Tags or None, optional
            If set, only include days that have all of the given tags.
        exclude_tags : frozenset of Tags or None, optional
            If set, exclude days that have any of the given tags.
        limit : int or None, optional
            If set, limit the number of returned days.
        order : {'asc', 'desc'}, default 'asc'
            The sort order of the returned days by date.

        Returns
        -------
        tuple of Day
            The matching days for the given MIC and date range.
        """
        return _get_days(
            mic,
            pd.Timestamp(start),
            pd.Timestamp(end),
            business_day,
            frozenset(include_tags) if include_tags else include_tags,
            frozenset(exclude_tags) if exclude_tags else exclude_tags,
            limit,
            order,
        )

    @router.get(
        "/exchanges/{mic}/days/{day}",
        tags=["Days"],
        summary="Describe a day on an exchange.",
        description="Returns the description of the given day on the given exchange.",
        operation_id="getExchangeDay",
        responses={200: {"description": "Description of the day on the exchange."}},
        response_model_exclude_none=True,
    )
    def get_exchange_day(
        mic: SupportedMIC,
        day: dt.date,
    ) -> Day:
        """
        Describe the given day on the given exchange.

        Parameters
        __________
        mic : SupportedMIC
            The exchange.
        day : dt.date
            The day to describe.

        Returns
        -------
        Day
            The description of the given day on the given exchange.
        """
        days = _get_days(mic, pd.Timestamp(day), pd.Timestamp(day))
        assert len(days) == 1
        return days[0]

    @router.get(
        "/exchanges/{mic}/days/{day}/next",
        tags=["Days"],
        summary="Get the next days matching criteria relative to a day on an exchange.",
        description="Get the next days matching criteria relative to a day on an exchange.",
        operation_id="listNextExchangeDays",
        responses={
            200: {
                "description": "List of next days matching criteria relative to the day on the exchange."
            }
        },
        response_model_exclude_none=True,
    )
    def list_next_exchange_days(
        mic: SupportedMIC,
        day: dt.date,
        direction: Literal["forward", "backward"] = "forward",
        inclusive: bool = True,
        end: dt.date | None = None,
        business_day: bool | None = None,
        include_tags: Annotated[list[Tags] | None, Query()] = None,
        exclude_tags: Annotated[list[Tags] | None, Query()] = None,
        limit: Annotated[int, Field(gt=0)] | None = None,
        order: Literal["asc", "desc"] = "asc",
    ) -> tuple[Day, ...]:
        """
        Describe the given day on the given exchange.

        Parameters
        ----------
        mic : SupportedMIC
            The MIC of the exchange.
        day : pd.Timestamp
            The start of the period (inclusive).
        direction : Literal['forward', 'backward']
            The direction to search in relative to the day.
        inclusive : bool
            If set, the day itself is included in the searched date range.
        end : pd.Timestamp
            The end of the date range to search (inclusive).
        business_day : bool or None, optional
            If set, only include (non) business days.
        include_tags : frozenset of Tags or None, optional
            If set, only include days that have all of the given tags.
        exclude_tags : frozenset of Tags or None, optional
            If set, exclude days that have any of the given tags.
        limit : int or None, optional
            If set, limit the number of returned days.
        order : {'asc', 'desc'}, default 'asc'
            The sort order of the returned days by date.

        Returns
        -------
        tuple of Day
            The matching days for the given MIC and date range.
        """
        start = pd.Timestamp(day)
        if not inclusive:
            start = start + pd.Timedelta(days=(1 if direction == "forward" else -1))
        if direction == "backward":
            # For backward search, we want to search from 'day' down to 'end'
            # The 'end' parameter serves as the lower bound
            lower_bound = (
                pd.Timestamp(end)
                if end
                else (pd.Timestamp.min + pd.Timedelta(days=1)).normalize()
            )
            # Swap so _get_days processes from lower_bound up to start
            start, end = lower_bound, start
        else:
            end = pd.Timestamp(end) if end else pd.Timestamp.max.normalize()
        order0 = "asc" if direction == "forward" else "desc"

        result = _get_days(
            mic,
            start,
            end,
            business_day,
            frozenset(include_tags) if include_tags else include_tags,
            frozenset(exclude_tags) if exclude_tags else exclude_tags,
            limit,
            order0,
        )

        if order != order0:
            result = tuple(reversed(result))

        return result

    return router
