from collections.abc import Iterable

import exchange_calendars as ec
import pandas as pd
from cachetools import LFUCache, cached
from exchange_calendars_extensions.core import ExtendedExchangeCalendar
from exchange_calendars_extensions.core.util import get_weekmask_periods

REGULAR_SLOTS = (
    "day",
    "holidays_all",
    "regular_holidays",
    "adhoc_holidays",
    "special_opens_all",
    "special_opens",
    "special_opens_adhoc",
    "special_closes_all",
    "special_closes",
    "special_closes_adhoc",
    "quarterly_expiries",
    "monthly_expiries",
    "last_trading_days_of_months",
    "tz",
    "open_times",
    "close_times",
    "weekmask",
    "special_weekmasks",
    "meta",
    "weekend_days",
    "week_days",
)

EXTRA_SLOTS = ("open_times0", "close_times0", "weekmask_periods")

SLOTS = REGULAR_SLOTS + EXTRA_SLOTS


class ExtendedExchangeCalendarWrapper:
    """Wrapper class that exposes just a subset of the attributes of ExtendedExchangeCalendar. The names of the
    attributes are given as a static tuple from which the corresponding properties are created. Also, the wrapper should
    not hold a reference to the wrapped object, so that the wrapped object and its unneeded properties can be garbage
    collected when no longer needed."""

    # The names of the properties to expose.
    __slots__ = SLOTS

    def __init__(self, exchange_calendar: ExtendedExchangeCalendar):
        # Copy all the relevant properties from wrapped object to this one.
        for prop in REGULAR_SLOTS:
            if hasattr(exchange_calendar, prop):
                setattr(self, prop, getattr(exchange_calendar, prop))

        self.open_times0 = tuple(
            (d if d is not None else pd.Timestamp.min, t)
            for d, t in exchange_calendar.open_times
        )

        self.close_times0 = tuple(
            (d if d is not None else pd.Timestamp.min, t)
            for d, t in exchange_calendar.close_times
        )

        self.weekmask_periods = get_weekmask_periods(exchange_calendar)


class ExchangeCalendarCache:
    """Cache for exchange calendars. The cache is populated on demand, and the instances are cached using a least
    frequently used cache."""

    def __init__(self, mics: Iterable[str]):
        # Set up caching for get() method.
        cache = LFUCache(maxsize=len([mic for mic in mics]))
        self.get = cached(cache=cache)(self.get)

        # Warm up cache.
        for mic in mics:
            _ = self.get(mic)

    def get(self, mic: str) -> ExtendedExchangeCalendarWrapper:
        # Get wrapper for the given MIC.
        c = ExtendedExchangeCalendarWrapper(ec.get_calendar(mic))

        # Clear out exchange_calendars internal cache to purge the instance created above. Rationale:
        # Reduces memory footprint, and we have already extracted all needed members into our own structure. If not
        # done here after each calendar, multiple instances may accumulate in the internal cache and may use substantial
        # amounts of memory.
        ec.calendar_utils.global_calendar_dispatcher._calendars.clear()

        return c

    def refresh(self, mic: str) -> None:
        key = (mic,)
        if key in self.get.cache:
            self.get.cache.pop(key)
        _ = self.get(mic)
