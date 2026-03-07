import datetime as dt
import enum
import heapq
import itertools
import re
from collections.abc import Callable
from datetime import date, datetime, timedelta, timezone, tzinfo
from enum import Enum
from typing import Annotated, Literal, Union
from zoneinfo import ZoneInfo

import pandas as pd
from cachetools import LFUCache, cached
from fastapi import APIRouter, HTTPException, Query, Security
from pandas import Timestamp
from pydantic import BaseModel, Field

from exchange_calendar_service.app.auth import AuthenticatedUser
from exchange_calendar_service.app.deps import authorization
from exchange_calendar_service.core.common.context import Context
from exchange_calendar_service.core.common.util import get_enum_key_literal_type
from exchange_calendar_service.core.util import find_interval


def _parse_tz(tz_str: str | None) -> tzinfo:
    """Parse timezone string to tzinfo.

    Accepts:
    - IANA names: "UTC", "America/New_York", "Europe/London", etc.
    - UTC offsets: "+00:00", "+05:30", "-08:00", etc.

    Returns:
        A tzinfo object (ZoneInfo or fixed-offset timezone).

    Raises:
        ValueError: If the timezone string is invalid.
    """
    if tz_str is None:
        raise ValueError("Timezone string cannot be None")

    # Try UTC offset format: [+/-]HH:MM.
    offset_pattern = r"^([+-])(\d{2}):(\d{2})$"
    match = re.match(offset_pattern, tz_str)
    if match:
        sign = 1 if match.group(1) == "+" else -1
        hours = int(match.group(2))
        minutes = int(match.group(3))
        offset = timedelta(hours=sign * hours, minutes=sign * minutes)
        return timezone(offset)

    # Try IANA timezone name.
    try:
        return ZoneInfo(tz_str)
    except Exception as e:
        raise ValueError(f"Invalid timezone: {tz_str}") from e


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


class Session(BaseModel):
    open: dt.time = Field(title="The start of the trading session (HH:MM:SS).")
    close: dt.time = Field(title="The end of the trading session (HH:MM:SS).")


class BusinessDay(BaseModel):
    date: dt.date = Field(title="The date of the day in ISO format (YYYY-MM-DD).")
    name: str | None = Field(title="The name of the day.", default=None)
    business_day: Literal[True] = Field(
        title="Indicates that the day is a business day.", default=True
    )
    session: Session = Field(title="The trading session.")
    tags: set[Tags] = Field(title="A set of tags associated with the day.")


class NonBusinessDay(BaseModel):
    date: dt.date = Field(title="The date of the day in ISO format (YYYY-MM-DD).")
    name: str | None = Field(title="The name of the day.", default=None)
    business_day: Literal[False] = Field(
        title="Indicates that the day is not a business day.", default=False
    )
    tags: set[Tags] = Field(title="A set of tags associated with the day.")


Day = Annotated[Union[BusinessDay, NonBusinessDay], Field(discriminator="business_day")]


# Instants API models
class Interval(BaseModel):
    """Half-open interval [start, end) in the target timezone."""

    start: datetime
    end: datetime


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

    # Multi-exchange response types
    MultiExchangeDay = dict[str, Day]
    MultiExchangeDays = list[MultiExchangeDay]

    class BusinessDayInstant(BaseModel):
        """Business day with trading session."""

        mic: SupportedMIC
        day_interval: Interval
        session_interval: Interval
        name: str | None = None
        business_day: Literal[True] = True
        tags: set[Tags] = Field(default_factory=set)

    class NonBusinessDayInstant(BaseModel):
        """Non-business day (holiday/weekend) - no session."""

        mic: SupportedMIC
        day_interval: Interval
        name: str | None = None
        business_day: Literal[False] = False
        tags: set[Tags] = Field(default_factory=set)

    DayInstant = Annotated[
        Union[BusinessDayInstant, NonBusinessDayInstant],
        Field(discriminator="business_day"),
    ]

    DayInstantsByExchange = dict[SupportedMIC, list[DayInstant]]
    DayInstantsList = list[DayInstant]

    router = APIRouter()

    @router.get(
        "/exchanges",
        tags=["Reference"],
        summary="Get a list of supported exchange codes, i.e. MICs.",
        description="Returns the list of supported MICs.",
        operation_id="getExchanges",
        responses={200: {"description": "List of supported MICs."}},
    )
    async def get_exchanges(
        _: AuthenticatedUser = Security(authorization, scopes=["exchanges:read"]),
    ) -> SupportedMICs:
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
    async def get_exchange_info(
        mic: SupportedMIC,
        _: AuthenticatedUser = Security(authorization, scopes=["exchange:info:read"]),
    ) -> ExchangeInfo:
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

    def _get_days_multi(
        mics: tuple[SupportedMIC, ...],
        start: pd.Timestamp,
        end: pd.Timestamp,
        business_day: bool | None = None,
        include_tags: frozenset[Tags] | None = None,
        exclude_tags: frozenset[Tags] | None = None,
        limit: Annotated[int, Field(gt=0)] | None = None,
        order: Literal["asc", "desc"] = "asc",
    ) -> MultiExchangeDays:
        """
        Get days for multiple MICs, grouped by date.

        Returns a list where each element is a dict mapping MIC to Day for a specific date.
        MICs within each date are ordered alphabetically.

        Parameters
        ----------
        mics : tuple of SupportedMIC
            The MICs of the exchanges to query.
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
            If set, limit the number of returned date records.
        order : {'asc', 'desc'}, default 'asc'
            The sort order of the returned days by date.

        Returns
        -------
        MultiExchangeDays
            List of dicts, each mapping MIC to Day for a specific date.
        """
        # Get days for each MIC
        mic_to_days: dict[SupportedMIC, dict[dt.date, Day]] = {}
        for mic in mics:
            days = _get_days(
                mic,
                start,
                end,
                business_day,
                include_tags,
                exclude_tags,
                limit,
                order,
            )
            mic_to_days[mic] = {d.date: d for d in days}

        # Collect all unique dates across all MICs
        all_dates: set[dt.date] = set()
        for days_dict in mic_to_days.values():
            all_dates.update(days_dict.keys())

        # Sort dates according to order
        sorted_dates = sorted(all_dates, reverse=order == "desc")

        # Apply limit early to avoid unnecessary work
        if limit is not None:
            sorted_dates = sorted_dates[:limit]

        # Build result grouped by date
        result: MultiExchangeDays = []
        for d in sorted_dates:
            date_entry: MultiExchangeDay = {}
            # Sort MICs alphabetically for consistent ordering
            for mic in sorted(mics):
                if d in mic_to_days[mic]:
                    date_entry[mic] = mic_to_days[mic][d]
            if date_entry:  # Only add if at least one MIC has data for this date
                result.append(date_entry)

        return result

    @router.get(
        "/exchanges/{mic}/days",
        tags=["Single Exchange"],
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
    async def list_exchange_days(
        mic: SupportedMIC,
        start: dt.date,
        end: dt.date,
        business_day: bool | None = None,
        include_tags: Annotated[list[Tags] | None, Query()] = None,
        exclude_tags: Annotated[list[Tags] | None, Query()] = None,
        order: Literal["asc", "desc"] = "asc",
        limit: Annotated[int, Field(gt=0)] | None = None,
        _: AuthenticatedUser = Security(authorization, scopes=["exchange:days:read"]),
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
        tags=["Single Exchange"],
        summary="Describe a day on an exchange.",
        description="Returns the description of the given day on the given exchange.",
        operation_id="getExchangeDay",
        responses={200: {"description": "Description of the day on the exchange."}},
        response_model_exclude_none=True,
    )
    async def get_exchange_day(
        mic: SupportedMIC,
        day: dt.date,
        _: AuthenticatedUser = Security(authorization, scopes=["exchange:days:read"]),
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
        tags=["Single Exchange"],
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
    async def list_next_exchange_days(
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
        _: AuthenticatedUser = Security(authorization, scopes=["exchange:days:read"]),
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
        order0: Literal["asc", "desc"] = "asc" if direction == "forward" else "desc"

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

    @router.get(
        "/days",
        tags=["Multiple Exchanges"],
        summary="Get days in a date range that match criteria for multiple exchanges.",
        description=r"""For multiple exchanges, this endpoint returns the list of days in a given date range that match the given criteria.

Start and end date are mandatory and inclusive.

The `mics` parameter is a repeatable query parameter for specifying one or more MIC codes.

Filter criteria are optional:
- `business_day`: If set, only include (non) business days.
- `include_tags`: If set, only include days that have at least one of the given tags.
- `exclude_tags`: If set, exclude days that have any of the given tags.

Sorting and limiting are optional:
- `order`: The sort order of the returned days by date (default: ascending).
- `limit`: If set, limit the number of returned date records.

Note: The `limit` parameter applies to the number of date records returned. Each record contains data for all requested MICs that have data for that date. MICs within each date record are ordered alphabetically.
""",
        operation_id="listDays",
        responses={
            200: {
                "description": "List of days matching the criteria for multiple exchanges."
            }
        },
        response_model_exclude_none=True,
    )
    async def list_days(
        mics: Annotated[
            list[SupportedMIC],
            Query(title="MIC codes", description="One or more MIC codes to query."),
        ],
        start: dt.date,
        end: dt.date,
        business_day: bool | None = None,
        include_tags: Annotated[list[Tags] | None, Query()] = None,
        exclude_tags: Annotated[list[Tags] | None, Query()] = None,
        order: Literal["asc", "desc"] = "asc",
        limit: Annotated[int, Field(gt=0)] | None = None,
        _: AuthenticatedUser = Security(authorization, scopes=["days:read"]),
    ) -> MultiExchangeDays:
        """
        Get days for multiple exchanges in a date range.

        Parameters
        ----------
        mics : list of SupportedMIC
            The MICs of the exchanges to query.
        start : dt.date
            The start of the period (inclusive).
        end : dt.date
            The end of the period (inclusive).
        business_day : bool or None, optional
            If set, only include (non) business days.
        include_tags : list of Tags or None, optional
            If set, only include days that have all of the given tags.
        exclude_tags : list of Tags or None, optional
            If set, exclude days that have any of the given tags.
        order : {'asc', 'desc'}, default 'asc'
            The sort order of the returned days by date.
        limit : int or None, optional
            If set, limit the number of returned date records.

        Returns
        -------
        MultiExchangeDays
            List of dicts, each mapping MIC to Day for a specific date.
        """
        return _get_days_multi(
            tuple(mics),
            pd.Timestamp(start),
            pd.Timestamp(end),
            business_day,
            frozenset(include_tags) if include_tags else include_tags,
            frozenset(exclude_tags) if exclude_tags else exclude_tags,
            limit,
            order,
        )

    @router.get(
        "/days/{day}",
        tags=["Multiple Exchanges"],
        summary="Get a specific day for multiple exchanges.",
        description=r"""For multiple exchanges, returns the description of the given day.

The `mics` parameter is a repeatable query parameter for specifying one or more MIC codes.
""",
        operation_id="getDay",
        responses={200: {"description": "Description of the day for each exchange."}},
        response_model_exclude_none=True,
    )
    async def get_day(
        mics: Annotated[
            list[SupportedMIC],
            Query(title="MIC codes", description="One or more MIC codes to query."),
        ],
        day: dt.date,
        _: AuthenticatedUser = Security(authorization, scopes=["days:read"]),
    ) -> MultiExchangeDay:
        """
        Get a specific day for multiple exchanges.

        Parameters
        ----------
        mics : list of SupportedMIC
            The MICs of the exchanges to query.
        day : dt.date
            The day to describe.

        Returns
        -------
        MultiExchangeDay
            Dict mapping MIC to Day for the specific date.
        """
        days = _get_days_multi(
            tuple(mics),
            pd.Timestamp(day),
            pd.Timestamp(day),
            None,
            None,
            None,
            None,
            "asc",
        )
        assert len(days) == 1
        return days[0]

    @router.get(
        "/days/{day}/next",
        tags=["Multiple Exchanges"],
        summary="Get the next days matching criteria relative to a day for multiple exchanges.",
        description="Get the next days matching criteria relative to a day for multiple exchanges.",
        operation_id="listNextDays",
        responses={
            200: {
                "description": "List of next days matching criteria relative to the day for multiple exchanges."
            }
        },
        response_model_exclude_none=True,
    )
    async def list_next_days(
        mics: Annotated[
            list[SupportedMIC],
            Query(title="MIC codes", description="One or more MIC codes to query."),
        ],
        day: dt.date,
        direction: Literal["forward", "backward"] = "forward",
        inclusive: bool = True,
        end: dt.date | None = None,
        business_day: bool | None = None,
        include_tags: Annotated[list[Tags] | None, Query()] = None,
        exclude_tags: Annotated[list[Tags] | None, Query()] = None,
        limit: Annotated[int, Field(gt=0)] | None = None,
        order: Literal["asc", "desc"] = "asc",
        _: AuthenticatedUser = Security(authorization, scopes=["days:read"]),
    ) -> MultiExchangeDays:
        """
        Get the next days matching criteria relative to a day for multiple exchanges.

        Parameters
        ----------
        mics : list of SupportedMIC
            The MICs of the exchanges to query.
        day : dt.date
            The start of the period (inclusive).
        direction : {'forward', 'backward'}, default 'forward'
            The direction to search in relative to the day.
        inclusive : bool, default True
            If set, the day itself is included in the searched date range.
        end : dt.date or None, optional
            The end of the date range to search (inclusive).
        business_day : bool or None, optional
            If set, only include (non) business days.
        include_tags : list of Tags or None, optional
            If set, only include days that have all of the given tags.
        exclude_tags : list of Tags or None, optional
            If set, exclude days that have any of the given tags.
        limit : int or None, optional
            If set, limit the number of returned date records.
        order : {'asc', 'desc'}, default 'asc'
            The sort order of the returned days by date.

        Returns
        -------
        MultiExchangeDays
            List of dicts, each mapping MIC to Day for a specific date.
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
            # Swap so _get_days_multi processes from lower_bound up to start
            start, end = lower_bound, start
        else:
            end = pd.Timestamp(end) if end else pd.Timestamp.max.normalize()
        order0: Literal["asc", "desc"] = "asc" if direction == "forward" else "desc"

        result = _get_days_multi(
            tuple(mics),
            start,
            end,
            business_day,
            frozenset(include_tags) if include_tags else include_tags,
            frozenset(exclude_tags) if exclude_tags else exclude_tags,
            limit,
            order0,
        )

        if order != order0:
            result = list(reversed(result))

        return result

    @router.get(
        "/instants",
        tags=["Instants"],
        summary="Get days/sessions overlapping a timestamp range for multiple exchanges.",
        description=r"""For multiple exchanges, returns days/sessions that overlap with the given timestamp range.

The `mics` parameter is a repeatable query parameter for specifying one or more MIC codes.

The `start` and `end` parameters are ISO 8601 timestamps with timezone. The range is half-open: [start, end).

The `tz` parameter specifies the target timezone for returned instants. Can be:
- An IANA timezone name (e.g., "UTC", "America/New_York", "Europe/London")
- A UTC offset (e.g., "+00:00", "+05:30", "-08:00")

If `tz` is omitted, it will be inferred from the `start` and `end` parameters if they have the same timezone.
Otherwise, a 400 error is returned.

Filter criteria are optional:
- `business_day`: If set, only include (non) business days.
- `include_tags`: If set, only include days that have all of the given tags.
- `exclude_tags`: If set, exclude days that have any of the given tags.

The `orient` parameter controls the response format:
- `list` (default): Returns a flat list sorted by day_interval.start.
- `exchange`: Returns a dict mapping MIC to list of days (includes empty lists for MICs with no matches).
""",
        operation_id="listInstants",
        responses={
            200: {
                "description": "List of days/sessions matching the criteria for multiple exchanges."
            },
            400: {"description": "Bad request - e.g., ambiguous timezone."},
        },
        response_model_exclude_none=True,
    )
    async def list_instants(
        mics: Annotated[
            list[SupportedMIC],
            Query(title="MIC codes", description="One or more MIC codes to query."),
        ],
        start: datetime,
        end: datetime,
        tz: Annotated[
            str | None, Query(description="Target timezone (IANA name or UTC offset)")
        ] = None,
        business_day: bool | None = None,
        include_tags: Annotated[list[Tags] | None, Query()] = None,
        exclude_tags: Annotated[list[Tags] | None, Query()] = None,
        orient: Literal["list", "exchange"] = "list",
        _: AuthenticatedUser = Security(authorization, scopes=["instants:read"]),
    ) -> DayInstantsList | DayInstantsByExchange:
        """
        Get days/sessions overlapping a timestamp range for multiple exchanges.

        Parameters
        ----------
        mics : list of SupportedMIC
            The MICs of the exchanges to query.
        start : datetime
            The start of the query range (inclusive). Must be timezone-aware.
        end : datetime
            The end of the query range (exclusive). Must be timezone-aware.
        tz : str or None, optional
            Target timezone for returned instants. If None, inferred from start/end.
        business_day : bool or None, optional
            If set, only include (non) business days.
        include_tags : list of Tags or None, optional
            If set, only include days that have all of the given tags.
        exclude_tags : list of Tags or None, optional
            If set, exclude days that have any of the given tags.
        orient : {'list', 'exchange'}, default 'list'
            Response format. 'list' returns flat list, 'exchange' returns dict by MIC.

        Returns
        -------
        DayInstantsList or DayInstantsByExchange
            Days/sessions overlapping the query range, in requested format.
        """
        # Validate start/end are timezone-aware.
        if start.tzinfo is None or end.tzinfo is None:
            raise HTTPException(
                status_code=400,
                detail="start and end must be timezone-aware",
            )

        # Determine target timezone.
        if tz is None:
            if start.tzinfo == end.tzinfo:
                target_tz = start.tzinfo
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Timezone parameter (tz) is required when start and end have different timezones.",
                )
        else:
            target_tz = _parse_tz(tz)

        # Convert start/end to pandas timestamps.
        query_start = pd.Timestamp(start)
        query_end = pd.Timestamp(end)

        # Collect results for each MIC.
        results_by_mic: dict[SupportedMIC, list[DayInstant]] = {mic: [] for mic in mics}

        for mic in mics:
            c = Context().cache.get(mic)
            exchange_tz = c.tz

            # Expand query range to cover all potential days. Convert query boundaries to exchange timezone to find date
            # range.
            query_start_exch = query_start.tz_convert(exchange_tz)
            query_end_exch = query_end.tz_convert(exchange_tz)

            # Get the date range in exchange timezone (expand by 1 day on each side to be safe)
            date_start = query_start_exch.floor("D")
            date_end = query_end_exch.ceil("D")

            # Get all days in this range. _get_days expects naive timestamps or dates, so we convert to date.
            days = _get_days(
                mic,
                pd.Timestamp(date_start.date()),
                pd.Timestamp(date_end.date()),
                business_day=business_day,  # Get all, filter later
                include_tags=frozenset(include_tags) if include_tags else include_tags,
                exclude_tags=frozenset(exclude_tags) if exclude_tags else exclude_tags,
                limit=None,
                order="asc",
            )

            # Check each day for overlap with query range
            for day in days:
                # Get the date in exchange timezone.
                day_date = pd.Timestamp(day.date, tz=exchange_tz)

                # Calculate day_interval (midnight to midnight in exchange timezone).
                day_start = day_date.floor("D")
                day_end = day_start + pd.Timedelta(days=1)

                # Check if day_interval overlaps with query range. Overlap exists when day_start < query_end and
                # day_end > query_start
                if not (day_start < query_end and day_end > query_start):
                    continue

                # Apply filters.
                # day_tags = day.tags
                # if business_day is not None and day.business_day != business_day:
                #     continue
                # if include_tags and not any(tag in day_tags for tag in include_tags):
                #     continue
                # if exclude_tags and any(tag in day_tags for tag in exclude_tags):
                #     continue

                # Convert day_interval to target timezone
                day_interval_start = day_start.tz_convert(target_tz).to_pydatetime()
                day_interval_end = day_end.tz_convert(target_tz).to_pydatetime()

                day_instant: DayInstant

                # Create DayInstant
                if isinstance(day, BusinessDay):
                    # Calculate session_interval in target timezone. Session times are wall-clock times in exchange
                    # timezone.
                    session_open_time = day.session.open
                    session_close_time = day.session.close

                    session_interval_start = (
                        day_date.replace(
                            hour=session_open_time.hour,
                            minute=session_open_time.minute,
                            second=session_open_time.second,
                        )
                        .tz_convert(target_tz)
                        .to_pydatetime()
                    )
                    session_interval_end = (
                        day_date.replace(
                            hour=session_close_time.hour,
                            minute=session_close_time.minute,
                            second=session_close_time.second,
                        )
                        .tz_convert(target_tz)
                        .to_pydatetime()
                    )

                    day_instant = BusinessDayInstant(
                        mic=mic,
                        day_interval=Interval(
                            start=day_interval_start,
                            end=day_interval_end,
                        ),
                        session_interval=Interval(
                            start=session_interval_start,
                            end=session_interval_end,
                        ),
                        name=day.name,
                        tags=day.tags,
                    )
                else:
                    day_instant = NonBusinessDayInstant(
                        mic=mic,
                        day_interval=Interval(
                            start=day_interval_start,
                            end=day_interval_end,
                        ),
                        name=day.name,
                        tags=day.tags,
                    )

                results_by_mic[mic].append(day_instant)

        # Sort results by day_interval.start within each MIC.
        for mic in results_by_mic:
            results_by_mic[mic].sort(key=lambda d: d.day_interval.start)

        # Return based on orient.
        if orient == "exchange":
            return results_by_mic
        else:  # orient == "list"
            return list(
                heapq.merge(
                    *results_by_mic.values(), key=lambda d: d.day_interval.start
                )
            )

    return router
