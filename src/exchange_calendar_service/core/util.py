from collections.abc import Iterable

import exchange_calendars as ec


class ExchangeCalendarProxy:
    """
    A proxy for an exchange_calendar.ExchangeCalendar instance that only retains certain properties without keeping
    a reference to the underlying instance.
    """

    # Properties to copy from exchange_calendar to ExchangeCalendarProxy.
    PROPERTIES = (
        "day",
        "holidays_all",
        "special_opens_all",
        "special_closes_all",
        "tz",
        "open_times",
        "close_times",
        "weekmask",
        "monthly_expiries",
        "quarterly_expiries",
    )

    def __init__(self, exchange_calendar: ec.ExchangeCalendar) -> None:
        # Copy the properties from exchange_calendar to this instance.
        for prop in self.PROPERTIES:
            setattr(self, prop, getattr(exchange_calendar, prop))

        # Don't retain the reference to exchange_calendar so that it and all un-referenced properties can be garbage
        # collected. This is important because each instance of ec.ExchangeCalendar instantiates all session minutes
        # by default, which is a lot of memory.
        return


class ExchangeCalendars:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._proxies = {}
        return cls._instance

    def _make_calendar_proxy(self, key: str) -> ExchangeCalendarProxy:
        # Resolve to canonical name.
        key = ec.resolve_alias(key)

        # Create new proxy.
        proxy = ExchangeCalendarProxy(ec.get_calendar(key))

        self._proxies[key] = proxy

        return proxy

    def ensure(self, keys: Iterable[str]):
        for key in keys:
            # Access the proxy to force it to be created, if necessary
            _ = self[key]

    def refresh(self, key: str) -> ExchangeCalendarProxy:
        # Purge the proxy for the given key, forcing it to be re-created on next access.
        self.clear(key)
        # Access the proxy to force it to be re-created and return.
        return self[key]

    def clear(self, key: str) -> None:
        # Purge the proxy for the given key, if it exists.
        self._proxies.pop(ec.resolve_alias(key), None)

    def __getitem__(self, key: str) -> ExchangeCalendarProxy:
        resolved = ec.resolve_alias(key)
        if resolved not in self._proxies:
            self._proxies[resolved] = self._make_calendar_proxy(key)
        return self._proxies[resolved]

    def __len__(self):
        return len(self._proxies)

    def __iter__(self):
        return iter(self._proxies)

    def keys(self):
        return self._proxies.keys()

    def values(self):
        return self._proxies.values()

    def items(self):
        return self._proxies.items()
