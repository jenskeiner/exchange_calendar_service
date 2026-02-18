import exchange_calendars as ec
import exchange_calendars_extensions.core as ex
import pytest

from exchange_calendar_service.core.util import ExchangeCalendarProxy, ExchangeCalendars

ex.apply_extensions()


@pytest.fixture
def exchange_calendar():
    return ec.get_calendar("XLON")


class TestExchangeCalendarProxy:
    def test_properties(self, exchange_calendar: ex.ExtendedExchangeCalendar) -> None:
        """
        Test that each property in the ExchangeCalendarProxy.PROPERTIES tuple is correctly copied from the
        exchange_calendar instance to the ExchangeCalendarProxy instance.

        Parameters
        ----------
        exchange_calendar : ec.ExchangeCalendar
            The exchange_calendar instance to test.

        Returns
        -------
        None
        """
        # Create an ExchangeCalendarProxy instance from the exchange_calendar instance.
        proxy = ExchangeCalendarProxy(exchange_calendar)
        # Test each property by comparing it to the corresponding property in the exchange_calendar instance.
        assert proxy.day == exchange_calendar.day
        # assert proxy.holidays_all == exchange_calendar.holidays_all
        # assert proxy.special_opens_all == exchange_calendar.special_opens_all
        # assert proxy.special_closes_all == exchange_calendar.special_closes_all
        assert proxy.tz == exchange_calendar.tz
        assert proxy.open_times == exchange_calendar.open_times
        assert proxy.close_times == exchange_calendar.close_times
        assert proxy.weekmask == exchange_calendar.weekmask
        # assert proxy.monthly_expiries == exchange_calendar.monthly_expiries
        # assert proxy.quarterly_expiries == exchange_calendar.quarterly_expiries


class TestExchangeCalendars:
    """
    A collection of tests for the ExchangeCalendars class.
    """

    @pytest.fixture
    def exchange_calendars(self):
        """
        A fixture that creates an instance of ExchangeCalendars with the NYSE and NASDAQ keys.
        """
        cache = ExchangeCalendars()
        cache.ensure(["XLON", "XSWX"])

        yield cache

        for key in list(cache.keys()):
            cache.clear(key)

    def test_singleton(self, exchange_calendars):
        """
        Test that only one instance of ExchangeCalendars is ever created.
        """
        assert exchange_calendars is ExchangeCalendars()

    def test_make_calendar_proxy(self, exchange_calendars):
        """
        Test that _make_calendar_proxy creates an ExchangeCalendarProxy for the given key.
        """
        proxy = exchange_calendars._make_calendar_proxy("XLON")
        assert isinstance(proxy, ExchangeCalendarProxy)

    def test_ensure(self, exchange_calendars):
        """
        Test that ensure creates ExchangeCalendarProxies for all given keys.
        """
        exchange_calendars.ensure(["CMES", "IEPA"])
        assert "CMES" in exchange_calendars.keys()
        assert "IEPA" in exchange_calendars.keys()

    def test_refresh(self, exchange_calendars):
        """
        Test that refresh purges and re-creates the ExchangeCalendarProxy for the given key.
        """
        proxy1 = exchange_calendars["XLON"]
        proxy2 = exchange_calendars.refresh("XLON")
        assert proxy1 is not proxy2

    def test_clear(self, exchange_calendars):
        """
        Test that clear purges the ExchangeCalendarProxy for the given key.
        """
        _ = exchange_calendars["XLON"]
        exchange_calendars.clear("XLON")
        assert "XLON" not in exchange_calendars

    def test_getitem(self, exchange_calendars):
        """
        Test that __getitem__ returns the ExchangeCalendarProxy for the given key.
        """
        proxy = exchange_calendars["XLON"]
        assert isinstance(proxy, ExchangeCalendarProxy)

    def test_len(self, exchange_calendars):
        """
        Test that __len__ returns the number of ExchangeCalendarProxies in the ExchangeCalendars instance.
        """
        assert len(exchange_calendars) == 2

    def test_iter(self, exchange_calendars):
        """
        Test that __iter__ returns an iterator over the keys of the ExchangeCalendarProxies in the ExchangeCalendars instance.
        """
        assert set(exchange_calendars) == {"XLON", "XSWX"}

    def test_keys(self, exchange_calendars):
        """
        Test that keys returns a view of the keys of the ExchangeCalendarProxies in the ExchangeCalendars instance.
        """
        assert set(exchange_calendars.keys()) == {"XLON", "XSWX"}

    def test_values(self, exchange_calendars):
        """
        Test that values returns a view of the ExchangeCalendarProxies in the ExchangeCalendars instance.
        """
        assert isinstance(
            next(iter(exchange_calendars.values())), ExchangeCalendarProxy
        )

    def test_items(self, exchange_calendars):
        """
        Test that items returns a view of the key-value pairs of the ExchangeCalendarProxies in the ExchangeCalendars instance.
        """
        assert set(exchange_calendars.items()) == {
            ("XLON", exchange_calendars["XLON"]),
            ("XSWX", exchange_calendars["XSWX"]),
        }
