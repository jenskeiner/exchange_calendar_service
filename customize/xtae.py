import pandas as pd
from exchange_calendars.exchange_calendar import SUNDAY, HolidayCalendar
from exchange_calendars.exchange_calendar_xtae import (
    XTAEExchangeCalendar as XTAEExchangeCalendarUpstream,
)
from pandas import DatetimeIndex, Series
from pandas.tseries.holiday import Holiday


# Helper class that wraps a Holiday instance and optionally filters out dates where the day of week matches a given value.
class _Holiday:
    def __init__(
        self,
        holiday: Holiday,
        ignore: int | None = None,
    ):
        self.holiday = holiday
        self.ignore = ignore

    def dates(
        self, start_date, end_date, return_name: bool = False
    ) -> Series | DatetimeIndex:
        dates: Series | DatetimeIndex = self.holiday.dates(
            start_date, end_date, return_name
        )
        if self.ignore is not None:
            # Remove dates where day of week matches ignore value.
            index = dates.index if isinstance(dates, pd.Series) else dates
            return dates[index.dayofweek != self.ignore]
        else:
            return dates


class XTAEExchangeCalendar(XTAEExchangeCalendarUpstream):
    @property
    def special_closes(self):
        # Return upstream calendar, but ensure that Sundays are not included.
        return [
            (x[0], HolidayCalendar([_Holiday(y, ignore=SUNDAY) for y in x[1].rules]))
            for x in super(XTAEExchangeCalendar, self).special_closes
            if not isinstance(x[1], int) or x[1] != SUNDAY
        ]

    @property
    def special_weekmasks(self):
        # The exclusion of Sundays only applies to the period before 2026-01-04 when XTAE switched to a Monday to Friday
        # schedule.
        return [
            (None, pd.Timestamp("2026-01-04"), "1111000"),
        ]
