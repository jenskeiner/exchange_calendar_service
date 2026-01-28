from collections.abc import Iterable

import exchange_calendars as ec
from cachetools import cached, LFUCache
from exchange_calendars_extensions.core import ExtendedExchangeCalendar


class ExtendedExchangeCalendarWrapper:
    """Wrapper class that exposes just a subset of the attributes of ExtendedExchangeCalendar. The names of the
    attributes are given as a static tuple from which the corresponding properties are created. Also, the wrapper should
    not hold a reference to the wrapped object, so that the wrapped object and its unneeded properties can be garbage
    collected when no longer needed."""

    # The names of the properties to expose.
    __slots__ = (
        "day",
        "regular_holidays",
        "adhoc_holidays",
        "special_opens",
        "special_opens_adhoc",
        "special_closes",
        "special_closes_adhoc",
        "quarterly_expiries",
        "monthly_expiries",
        "last_trading_days_of_months",
        "tz",
        "open_times",
        "close_times",
        "weekmask",
        "meta",
    )

    def __init__(self, exchange_calendar: ExtendedExchangeCalendar):
        # Copy all the relevant properties from wrapped object to this one.
        for prop in self.__slots__:
            setattr(self, prop, getattr(exchange_calendar, prop))


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
        self.get.cache.pop(self.get.cache_key(self, mic))
        _ = self.get(mic)
