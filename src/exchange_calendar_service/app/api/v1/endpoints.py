import datetime as dt
import enum
import itertools
from collections import OrderedDict
from collections.abc import Iterable
from enum import Enum
from typing import Annotated, Any, Literal
from typing import Union
from zoneinfo import ZoneInfo

import pandas as pd
from cachetools import cached, LFUCache
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field, Tag, Discriminator

from exchange_calendar_service.core.common.constants import (
    standardised_tz_names,
)
from exchange_calendar_service.core.common.context import Context
from exchange_calendar_service.core.common.util import get_enum_key_literal_type


@enum.unique
class DayTypeBusinessSpecial(str, Enum):
    SPECIAL_CLOSE = "special close"
    SPECIAL_OPEN = "special open"
    WITCHING = "witching"
    MONTHLY_EXPIRY = "monthly expiry"
    MONTH_END = "month end"
    MSCI_REBAL = "MSCI rebal"


@enum.unique
class DayTypeNonBusinessSpecial(str, Enum):
    HOLIDAY = "holiday"


@enum.unique
class DayTypeNonBusinessRegular(str, Enum):
    WEEKEND = "weekend"


@enum.unique
class DayTypeBusinessRegular(str, Enum):
    REGULAR = "regular"


regular_day_type = "regular"
weekend_day_type = "weekend"
witching_day_type = "witching"
monthly_expiry_day_type = "monthly expiry"
month_end_day_type = "month end"
holiday_day_type = "holiday"
special_open_day_type = "special open"
special_close_day_type = "special close"
msci_rebal_day_type = "MSCI rebal"
special_day_types = frozenset(
    {
        holiday_day_type,
        special_open_day_type,
        special_close_day_type,
        witching_day_type,
        monthly_expiry_day_type,
        month_end_day_type,
        msci_rebal_day_type,
    }
)

# frozenset that contains all members of DayTypeBusinessSpecial and DayTypeNonBusinessSpecial.
special_day_types2: set[Union[DayTypeBusinessSpecial, DayTypeNonBusinessSpecial]] = frozenset(
    itertools.chain([x for x in DayTypeBusinessSpecial], [x for x in DayTypeNonBusinessSpecial])
)
business_day_types2: set[Union[DayTypeBusinessRegular, DayTypeBusinessSpecial]] = frozenset(
    itertools.chain([x for x in DayTypeBusinessRegular], [x for x in DayTypeBusinessSpecial])
)

min_year = dt.date.today().year - 30

max_year = dt.date.today().year + 30


class DayTypeBusinessSpecial(str, Enum):
    SPECIAL_CLOSE = "special close"
    SPECIAL_OPEN = "special open"
    WITCHING = "witching"
    MONTHLY_EXPIRY = "monthly expiry"
    MONTH_END = "month end"
    MSCI_REBAL = "MSCI rebal"


class DayTypeNonBusinessSpecial(str, Enum):
    HOLIDAY = "holiday"


class StandardDayClassification(BaseModel, frozen=True):
    date: dt.date
    type: DayTypeBusinessRegular | DayTypeNonBusinessRegular | DayTypeBusinessSpecial | DayTypeNonBusinessSpecial
    is_business_day: bool
    name: str | None = None


class SpecialOpenCloseDayClassification(StandardDayClassification):
    time: dt.time = None
    type: Literal[DayTypeBusinessSpecial.SPECIAL_OPEN, DayTypeBusinessSpecial.SPECIAL_CLOSE]
    tz: Union[str, None] = None


def infer_day_classification_type(v: Any):
    # Check if value has a "time" field. If so, it's a special open/close day classification.
    if isinstance(v, dict):
        time = v.get("time")
    else:
        time = getattr(v, "time", None)

    if time is not None:
        return "special_close"
    else:
        return "standard"


DayClassification = Annotated[
    (
        Annotated[StandardDayClassification, Tag("standard")]
        | Annotated[SpecialOpenCloseDayClassification, Tag("special_close")]
    ),
    Discriminator(infer_day_classification_type),
]


def parse_timezone(tz: Union[str, ZoneInfo, None], mic: Union[str, None]) -> ZoneInfo:
    """
    pytz only supports time zones in Continent/City format consistently; abbreviations, like CET
    or IST, are only supported in some cases. Thus, if the request has specified a non-supported abbreviation, like
    SAST, this must be converted to Africa/Johannesburg (which is supported).

    tz: time zone to test
    mic: if tz is not specified, we can either default to None (if mic = None), or we can default to a time zone belonging
    to a given mic.
    """

    if isinstance(tz, ZoneInfo):
        return tz

    if tz is not None:
        try:
            # check if timezone, as entered, is supported. If so, use it.
            tz = ZoneInfo(tz)
        except Exception:
            # If time zone as entered is not supported, try to convert to Continent/City.
            candidates = [(region, tz) for region, tz in standardised_tz_names.items() if tz == tz.upper()]
            if len(candidates) != 1:
                # more than one match was made, so not sure
                # which location is referred to. Use default time zone of calendar
                tz = None
            else:
                tz = ZoneInfo(candidates.pop()[0])
    if tz is None and mic:
        calendar = Context().cache.get(mic)
        try:
            tz = ZoneInfo(standardised_tz_names.get(str(calendar.tz)))
        except Exception:
            tz = ZoneInfo(str(calendar.tz))
    elif tz is None and mic is None:
        tz = ZoneInfo("UTC")

    return tz


def localize_time(
    date: dt.date,
    time: dt.time,
    tz_input: ZoneInfo,
    tz_target: Union[ZoneInfo, None] = None,
) -> dt.time:
    """
    Localise a given time of day on a given day in a given time zone into the time of day in another given time zone.

    :param date: the date
    :param time: the time of day
    :param tz_input: the time zone of the given date/time combination
    :param tz_target: the time zone to convert the time of day to
    """
    if tz_target is None or tz_input == tz_target:
        return time
    else:
        # Note to self: Use tz.localize(datetime.datetime.combine(date, time)) instead of
        # datetime.datetime.combine(date, time, tzinfo=tz) since the latter can lead to incorrect results.
        return dt.datetime.combine(date, time).replace(tzinfo=tz_input).astimezone(tz_target).time()


def get_router(exchanges_enum: type[Enum]):
    # Collection of all supported MICs.
    MICS = tuple(sorted(exchanges_enum.__members__.keys()))

    # A string type that only allows supported MICs.
    SupportedMIC = get_enum_key_literal_type(exchanges_enum)

    # Type alias for a list that can only contain supported MICs, with examples.
    SupportedMICs = Annotated[list[SupportedMIC], Field(examples=[MICS])]

    class StandardDayClassificationWithMics(StandardDayClassification):
        mics: list[SupportedMIC]

    class SpecialOpenCloseDayClassificationWithMics(
        SpecialOpenCloseDayClassification, StandardDayClassificationWithMics
    ):
        pass

    DayClassificationWithMics = Annotated[
        (
            Annotated[StandardDayClassificationWithMics, Tag("standard")]
            | Annotated[SpecialOpenCloseDayClassificationWithMics, Tag("special_close")]
        ),
        Discriminator(infer_day_classification_type),
    ]

    class DayClassificationMap(BaseModel):
        date: dt.date
        classifications: list[DayClassificationWithMics]

    class TimeZoneInfo(BaseModel):
        mic: SupportedMIC
        tz: str = Field(examples=["CET", "WET", "Europe/Lisbon"])

    router = APIRouter()

    @router.get(
        "/mics",
        tags=["Venues"],
        summary="Get a list of valid MICs that can be used with endpoints.",
        operation_id="api.special_days.get_valid_mics",
        responses={200: {"description": "List of valid MICs."}},
    )
    async def get_valid_mics() -> SupportedMICs:
        """
        Return a list of valid MIC codes
        """
        return list(exchanges_enum.__members__.keys())

    @router.get(
        "/mic2name",
        tags=["Venues"],
        summary="Get a mapping of MICs to exchange names.",
        operation_id="api.special_days.get_mic2name_mapping",
        responses={200: {"description": "Dictionary of MICs to exchange names."}},
    )
    async def get_mic2name_mapping() -> (
        Annotated[
            dict[SupportedMIC, str],
            Field(examples=[{m: exchanges_enum[m].value for m in MICS}]),
        ]
    ):
        return {name: value for name, value in exchanges_enum.__members__.items()}

    @router.get(
        "/timezone",
        tags=["Venues"],
        summary="Get the time zone name for one or all valid operating MICs.",
        operation_id="api.special_days.get_timezone",
        responses={
            200: {
                "description": "List of MIC code and time zone code pairs. If `standardise` was set to `true` then "
                "the short time zone names reflect only the current time zone in effect. Standardised "
                "names make it possible to group together exchanges using the same time zone. If "
                "`standardise` was set to `false` then the time zone names returned accurately reflect "
                "the time zone over time. For example, the current time zone for XLIS is CET, but "
                "would have been WET for a period between 1992 and 1996. While returning CET for XLIS "
                "wouldn't reflect that, returning `Europe/Lisbon`, as happens when `standardise` is set "
                "to `false`, would."
            }
        },
    )
    @cached(LFUCache(2 * (len(MICS) + 1)))
    def get_timezone(mic: SupportedMIC = None, standardise: bool = True) -> list[TimeZoneInfo]:
        mics = (mic,) if mic is not None else MICS
        result = []
        for m in mics:
            # get trading calendar for given mic, e.g. XETR
            c = Context().cache.get(m)
            # get timezone for mic in Continent/City format, e.g. Europe/Berlin
            tz = c.tz
            if standardise:
                # map Continent/City tz to standard tz names, e.g. Europe/Berlin --> CET (not CEST)
                name = standardised_tz_names.get(str(tz), None)
                if name is not None:
                    tz = name
            result.append(TimeZoneInfo(mic=m, tz=str(tz)))
        return result

    @router.get(
        "/special_days",
        tags=["Days"],
        summary="Get a list of special days for a given operating MIC and year.",
        description="Get a list of special days for a given operating MIC and year. Special days are days that are "
        "neither regular business days nor regular days where the exchange is closed, i.e. weekend "
        "days. Special days may be business days, e.g. special close days, or non-business days, e.g. "
        "holidays.",
        operation_id="api.special_days.get_special_days",
        responses={200: {"description": "List of special days for the given operating MIC and year."}},
    )
    def get_special_days(
        mic: SupportedMIC, year: Union[int, None] = None, tz: Union[str, None] = None
    ) -> list[DayClassification]:
        """
        Returns a list of special days for a given operating MIC and year combination.

        Special days include regular holidays where the exchange is closed, special opens/closes where the trading hours
        deviate from the regular schedule, and witching days which have regular trading hours but typically see increased
        trading activity owing to options/futures expiry.

        Weekdays that are never regular trading days (typically Saturdays and Sundays) are never returned as special days.

        :param mic: the operating MIC to return the special days for
        :param year: the optional year to return special days for, defaults to the current year
        :param tz: the optional time zone to return special open/close times in, defaults to the native time zone for each
            exchange
        :return: special days for the given operating MIC and year combination
        """

        # To correctly handle the case where the year is omitted, need to get the year to use here every time rather than
        # use a default argument since those are instantiated only once when the method is created. Using a default argument
        # would lead to use of the wrong year if the service rolls over to a new calendar year. Also, to avoid problems
        # with caching in that area, defer to _get_special_days0() and don't wrap this method with a cache itself.
        return _get_special_days0(mic, year if year is not None else dt.date.today().year, tz)

    # Cache return values. Allow for two times the number of operating MICs.
    @cached(LFUCache(maxsize=2 * len(MICS)))
    def _get_special_days0(mic: SupportedMIC, year: int, tz: Union[str, None]) -> list[DayClassification]:
        """
        Helper method for get_special_days that gets the actual list of special days.

        :param mic: the operating MIC to return the special days for
        :param year: the year to return special days for
        :param tz: the time zone to return special open/close times in, if set to None, use the native time zone for each
            exchange
        :return: special days for the given operating MIC and year combination
        """

        # Get exchange calendar for MIC.
        c = Context().cache.get(mic)

        # If time zone name is given, convert to tzinfo. Otherwise, use calendar's time zone.
        tz: ZoneInfo = parse_timezone(tz=tz, mic=mic)

        # tz as str
        tz_str = str(tz)

        # List of special days.
        days = []

        # First day of year.
        s = dt.datetime(year, 1, 1)

        # Last day of year
        e = dt.datetime(year, 12, 31)

        # Add regular holidays.
        days.extend(
            [
                StandardDayClassification.model_validate(
                    {
                        "date": date.to_pydatetime().date(),
                        "type": holiday_day_type,
                        "is_business_day": False,
                        "name": name,
                    }
                )
                for date, name in c.regular_holidays.holidays(s, e, return_name=True).items()
            ]
        )

        # Add ad-hoc holidays.
        days.extend(
            [
                StandardDayClassification.model_validate(
                    {
                        "date": date.to_pydatetime().date(),
                        "type": holiday_day_type,
                        "is_business_day": False,
                        "name": "ad-hoc holiday",
                    }
                )
                for date in c.adhoc_holidays
                if date.year == year
            ]
        )

        # Add regular special closes.
        for time, cal in c.special_closes:
            days.extend(
                [
                    SpecialOpenCloseDayClassification.model_validate(
                        {
                            "date": date.to_pydatetime().date(),
                            "type": special_close_day_type,
                            "is_business_day": True,
                            "time": localize_time(date.to_pydatetime().date(), time, c.tz, tz).isoformat(),
                            "tz": tz_str,
                            "name": name,
                        }
                    )
                    for date, name in cal.holidays(s, e, return_name=True).items()
                ]
            )

        # Add ad-hoc special closes.
        for time, dates in c.special_closes_adhoc:
            days.extend(
                [
                    SpecialOpenCloseDayClassification.model_validate(
                        {
                            "date": x.date(),
                            "type": special_close_day_type,
                            "is_business_day": True,
                            "time": localize_time(x.date(), time, c.tz, tz).isoformat(),
                            "tz": tz_str,
                            "name": "ad-hoc special close",
                        }
                    )
                    for x in dates
                    if x.year == year
                ]
            )

        # Add regular special opens.
        for time, cal in c.special_opens:
            days.extend(
                [
                    SpecialOpenCloseDayClassification.model_validate(
                        {
                            "date": date.to_pydatetime().date(),
                            "type": special_open_day_type,
                            "is_business_day": True,
                            "time": localize_time(date.to_pydatetime().date(), time, c.tz, tz).isoformat(),
                            "tz": tz_str,
                            "name": name,
                        }
                    )
                    for date, name in cal.holidays(s, e, return_name=True).items()
                ]
            )

        # Add ad-hoc special opens.
        for time, dates in c.special_opens_adhoc:
            days.extend(
                [
                    SpecialOpenCloseDayClassification.model_validate(
                        {
                            "date": x.date(),
                            "type": special_open_day_type,
                            "is_business_day": True,
                            "time": localize_time(x.date(), time, c.tz, tz).isoformat(),
                            "tz": tz_str,
                            "name": "ad-hoc special open",
                        }
                    )
                    for x in dates
                    if x.year == year
                ]
            )

        # Quarterly expiries.
        days.extend(
            [
                StandardDayClassification.model_validate(
                    {
                        "date": date.to_pydatetime().date(),
                        "type": witching_day_type,
                        "is_business_day": True,
                        "name": name,
                    }
                )
                for date, name in c.quarterly_expiries.holidays(s, e, return_name=True).items()
            ]
        )

        # Monthly expiries.
        days.extend(
            [
                StandardDayClassification.model_validate(
                    {
                        "date": date.to_pydatetime().date(),
                        "type": monthly_expiry_day_type,
                        "is_business_day": True,
                        "name": name,
                    }
                )
                for date, name in c.monthly_expiries.holidays(s, e, return_name=True).items()
            ]
        )

        # All dates collected so far.
        dates = [x.date for x in days]

        # Add last trading day for every month, if not already collected.
        days.extend(
            [
                x
                for x in [
                    StandardDayClassification.model_validate(
                        {
                            "date": date.to_pydatetime().date(),
                            "type": month_end_day_type,
                            "is_business_day": True,
                            "name": name,
                        }
                    )
                    for date, name in c.last_trading_days_of_months.holidays(s, e, return_name=True).items()
                ]
                if x.date not in dates
            ]
        )

        # All dates collected so far.
        dates = [x.date for x in days]

        # MSCI rebalancing days.
        # days.extend([x for x in [{'date': check_date(c.day_merged, d), 'type': msci_rebal_day_type, 'is_business_day': True,
        #    'name': 'MSCI Rebalancing'} for d in get_msci_rebal_dates(year)] if
        #                x['date'] not in dates and x['date'] is not None])

        # Filter out days that fall on regular non-business days, i.e. weekend days.
        days = [x for x in days if c.weekmask[x.date.weekday()] == "1"]

        # Sort all days by date.
        days = sorted(days, key=lambda x: x.date)

        # for day in days:
        # Convert dates to ISO-format strings.
        # day['date'] = day['date'].isoformat()

        return days

    # Cache return values.
    @router.get(
        "/classify_day",
        tags=["Days"],
        summary="Classify a given day for one or all valid operating MICs.",
        operation_id="api.special_days.classify_day",
        responses={200: {"description": "List of classifications for the given day."}},
    )
    @cached(LFUCache(maxsize=50))
    def classify_day(
        day: dt.date, mic: SupportedMIC = None, tz: str | None = None
    ) -> Union[
        DayClassification,
        list[DayClassificationWithMics],
    ]:
        """
        Return classification of given day for a single MIC or all MICs combined.

        :param day: the datetime.date specifying the day to classify
        :param mic: the optional single MIC code to classify the day for
        :param tz: the optional name of the time zone to return special open/close times in
        :param return_mics: whether to return the list of MICs the classification was done for in the result. Defaults to True.
        """

        if mic is not None:
            # Classify for the single MIC.

            # Check for weekend.
            if Context().cache.get(mic).weekmask[day.weekday()] == "0":
                return StandardDayClassification(
                    date=day,
                    type=DayTypeNonBusinessRegular.WEEKEND,
                    is_business_day=False,
                )

            # Get special days for year.
            special_days: list[DayClassification] = get_special_days(mic, day.year, tz=tz)

            # Check for special day.
            for d in special_days:
                if d.date == day:
                    return d

            # If we get here, must be a regular trading day.
            return StandardDayClassification(date=day, type=DayTypeBusinessRegular.REGULAR, is_business_day=True)
        else:
            # Classify for all operating MICs.

            # Dictionary to map classifications to the corresponding list of MICs they apply to. The same day, e.g.,
            # 2020-12-24, may be classified as a special close day at different exchanges, but with different actual
            # closing times. These classifications should be treated as distinct.
            r: dict[DayClassification, list[SupportedMIC]] = {}

            # Loop over classifications for all operating MICs.
            for k, v in {mic: classify_day(day, mic=mic, tz=tz) for mic in MICS}.items():
                # Update entry for classification. Create one if necessary.
                m = r.get(v, [])
                m.append(k)
                r[v] = m

            # The list of classifications to return.
            r0 = []

            # Loop over all different classifications.
            for k, v in r.items():
                r0.append(DayClassificationWithMics(**k.model_dump(), mics=v))

            return r0

    @router.get(
        "/next_special_days",
        tags=["Days"],
        summary="Get the next/previous special days relative to a given day.",
        description="Get the next/previous special days relative to a given day. Special days are days that are "
        "neither regular business days nor regular days where the exchange is closed, i.e. weekend "
        "days. Special days may be business days, e.g. special close days, or non-business days, e.g. "
        "holidays.",
        operation_id="api.special_days.get_next_special_days",
        responses={
            200: {"description": "List of special days for the given operating MIC and year."},
            416: {"description": "Requested range is too large."},
        },
    )
    def get_next_special_days(
        day: dt.date = Query(default_factory=lambda: dt.date.today()),
        inclusive: bool = True,
        forward: bool = True,
        mic: list[SupportedMIC] = Query(default=None),
        types: set[DayTypeBusinessSpecial | DayTypeNonBusinessSpecial] = Query(default=special_day_types2),
        n: int = 1,
        range: int | None = None,
        tz: str | None = None,
        skip_bad_dates: bool = False,
    ) -> tuple[list[DayClassificationMap], int]:
        return _get_next_special_days0(
            day,
            inclusive,
            forward,
            frozenset(mic) if mic is not None else mic,
            frozenset(types) if types is not None else special_day_types2,
            n,
            range,
            tz,
            skip_bad_dates,
        )

    @router.get(
        "/next_business_days",
        tags=["Days"],
        summary="Get the next/previous business days relative to a given day.",
        description="Return a list of previous or upcoming business days relative to a given day. Note that business "
        "days include certain types of special days like special open/close days, or triple-witching "
        "days, i.e. any day on which an exchange is open for trading counts as a business day.",
        operation_id="api.special_days.get_next_business_days",
        responses={
            200: {"description": "List of business days sorted by increasing distance to the given day."},
            416: {"description": "Requested range is too large."},
        },
    )
    def get_next_business_days(
        day: dt.date = Query(default_factory=lambda: dt.date.today()),
        inclusive: bool = True,
        forward: bool = True,
        mic: list[SupportedMIC] = Query(default=None),
        types: set[DayTypeBusinessSpecial | DayTypeBusinessRegular] = Query(default=business_day_types2),
        n: int = 1,
        range: int | None = None,
        tz: str | None = None,
        skip_bad_dates: bool = False,
    ) -> tuple[list[DayClassificationMap], int]:
        return _get_next_special_days0(
            day,
            inclusive,
            forward,
            frozenset(mic) if mic is not None else mic,
            frozenset(types) if types is not None else business_day_types2,
            n,
            range,
            tz,
            skip_bad_dates,
        )

    def _get_business_days(mic: str, start: dt.datetime, end: dt.datetime) -> list[dt.date]:
        result = [x for x in pd.bdate_range(start, end, freq=Context().cache.get(mic).day).date]
        return result

    @cached(LFUCache(maxsize=20))
    def _get_next_special_days0(
        day: dt.date,
        inclusive: bool,
        forward: bool,
        mic: frozenset | None,
        types: frozenset | None,
        n: int,
        range: int | None,
        tz: str,
        skip_bad_dates: bool,
    ) -> tuple[list[DayClassificationMap], int]:
        result = dict()
        mics = mic if mic is not None else MICS
        valid_types = types if types is not None else special_day_types
        year = day.year
        needed = n
        range_threshold = (
            (dt.datetime.combine(date=day, time=dt.time.min) + dt.timedelta(days=(1 if forward else -1) * range)).date()
            if range is not None
            else None
        )
        status = 200
        # TODO: Catch situation where type isn't available, e.g. special close on XAMS.

        while needed > 0:
            # Build up a dictionary with dates as key to group together common dates. Each value is a dictionary that maps
            # day classifications to the list of MICs it applies to. This is because the same day may be a different type of
            # special day across the various exchanges.
            special_days = dict()

            for m in mics:
                # Get all special days for MIC for current year.
                special_days_for_mic: list[DayClassification] = get_special_days(m, year, tz=tz)

                # Filter special days for specified types, e.g. business days only (see valid_types variable)
                relevant_special_days_for_mic = [x for x in special_days_for_mic if x.type in valid_types]

                # If year is the same as that of day, then if forward is true (false), filter out all days that are before
                # (after) day, respecting the inclusive flag as well.
                if year == day.year:

                    def is_before(x, y):
                        if forward:
                            return x < y or (not inclusive and x == y)
                        else:
                            return x > y or (not inclusive and x == y)

                    relevant_special_days_for_mic = [
                        x for x in relevant_special_days_for_mic if not is_before(x.date, day)
                    ]

                # If regular business days are to be included, get those as well for year. But exclude those that are also
                # contained in the list of special days (e.g. triple witching days).
                if regular_day_type in valid_types:
                    # Determine the period for which to get the regular business days.
                    if year == day.year and forward:
                        start = dt.datetime(year, day.month, day.day) + dt.timedelta(days=0 if inclusive else 1)
                    else:
                        start = dt.datetime(year, 1, 1)

                    if year == day.year and not forward:
                        end = dt.datetime(year, day.month, day.day) - dt.timedelta(days=0 if inclusive else 1)
                    else:
                        end = dt.datetime(year, 12, 31)

                    # Get business days. This may include special days like e.g. early close days which are already included
                    # in special_days_for_mic.
                    business_days_for_mic: list[dt.date] = _get_business_days(m, start, end)

                    # Filter out business days that are already marked as special days.
                    special_days_for_mic_dates = [x.date for x in special_days_for_mic]

                    business_days_for_mic: list[StandardDayClassification] = [
                        StandardDayClassification(
                            date=x,
                            type=DayTypeBusinessRegular.REGULAR,
                            is_business_day=True,
                        )
                        for x in business_days_for_mic
                        if x not in special_days_for_mic_dates
                    ]

                    # Add regular business days to "special days".
                    relevant_special_days_for_mic.extend(business_days_for_mic)

                for d in relevant_special_days_for_mic:
                    # Get existing entry for date in dictionary.
                    v = special_days.get(d.date, dict())

                    # Get existing entry for classification.
                    c = v.get(d, list())

                    # Add the MIC code to the list.
                    c.append(m)

                    # Safe updated entry back to v.
                    v[d] = c

                    # Safe updated entry back to special_days.
                    special_days[d.date] = v

            # Remove bad dates, if specified
            if skip_bad_dates and not forward and len(special_days) > 0:
                # start and end are only set
                special_days = _remove_bad_days(mics=list(mics), special_days=special_days)

            # Sort dict by date (key)
            special_days = OrderedDict(sorted(special_days.items(), key=lambda x: x[0], reverse=not forward))

            # Filter out all days that are outside the requested range, maybe.
            if range_threshold is not None:
                special_days = OrderedDict(
                    filter(
                        lambda x: x[0] <= range_threshold if forward else x[0] >= range_threshold,
                        special_days.items(),
                    )
                )

            # Only retain number of items still needed, maybe.
            special_days = OrderedDict(itertools.islice(special_days.items(), min(needed, len(special_days))))

            # Append items to result.
            result.update(special_days)

            # Update number of items still needed.
            needed -= len(special_days)

            # Move on to next (previous) year.
            year += 1 if forward else -1

            # Check that new year is not already outside range, maybe.
            if range_threshold is not None:
                # The first day (relative to the search direction) in the new year.
                first = dt.date(day=1, month=1, year=year) if forward else dt.date(day=31, month=12, year=year)
                is_outside_range = first > range_threshold if forward else first < range_threshold
                if is_outside_range:
                    break

            # Check if we're outside the range of permissible values for year.. If not, assume that we can't find any more
            # relevant special days.
            if not min_year <= year <= max_year:
                status = 416
                break

        def combine(c: DayClassification, mics: list[str]) -> DayClassificationWithMics:
            if isinstance(c, StandardDayClassification):
                return StandardDayClassificationWithMics(**c.model_dump(), mics=mics)
            elif isinstance(c, SpecialOpenCloseDayClassification):
                return SpecialOpenCloseDayClassificationWithMics(**c.model_dump(), mics=mics)
            else:
                raise RuntimeError("Unexpected day classification type.")

        result = sorted(
            [
                DayClassificationMap(date=k, classifications=[combine(c, m) for c, m in v.items()])
                for k, v in result.items()
            ],
            key=lambda x: x.date,
            reverse=not forward,
        )

        return result, status

    def get_bad_dates(
        mic: Iterable[SupportedMIC] | None = None,
        start: dt.date | None = None,
        end: dt.date | None = None,
    ) -> Iterable[dt.date]:
        """
        Finds and returns bad dates for mic (if given), and within date range defined by start and end date.

        test_docs parameter only passed when running unit tests
        """

        if not end:
            # if no end date specified, use today, i.e. ignore any future bad dates.
            end = pd.Timestamp.now().date()

        if not start:
            # if no start date specified, use end - 365 days
            start = pd.Timestamp.now().date() - pd.Timedelta(years=1)

        mics = (mic,) if mic else MICS

        # filter for start and end dates, and MIC if applicable
        result = []

        for m in mics:
            # get bad dates for MIC
            result.extend(d for d, meta in Context().cache.get(m).meta(start=start, end=end) if "bad date" in meta.tags)

        return result

    def _remove_bad_days(
        mics: Iterable[SupportedMIC],
        special_days: dict[dt.date, dict[DayClassification, list[SupportedMIC]]],
        test_docs: list = None,
    ):
        """
        Remove bad days from return dates, when parameter skip_bad_dates is true

        the test_docs variable is only set to not None by unit tests
        """

        dates = list(special_days.keys())
        start, end = str(min(dates)), str(max(dates))

        # get bad dates for mic, as list
        bad_dates: Iterable[dt.date] = get_bad_dates(mic=mics, start=start, end=end, test_docs=test_docs)

        # iterate through bad dates found and filter out irrelevant dates and mics
        for item in bad_dates:
            mic = item["mic"]
            date = item["date"]

            if date in list(special_days.keys()):
                dateTypeKey = list(special_days[date].keys())[0]
                if mic in special_days[date][dateTypeKey]:
                    special_days[date][dateTypeKey].remove(mic)

        # update special days to remove "empty" dates
        special_days = {k: v for k, v in special_days.items() if list(v.values())[0] != []}

        return special_days

    return router
