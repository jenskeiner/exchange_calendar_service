import datetime as dt

from exchange_calendar_service.app.api.v1.endpoints import (
    BusinessCalendarDay,
    CalendarDaySession,
    NonBusinessCalendarDay,
    Tags,
)

# XAMS: 09:00-17:30
xams_2021 = [
    NonBusinessCalendarDay(
        date=dt.date(2021, 1, 1),
        name="New Year's Day",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 1, 15),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 1, 29),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 2, 19),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 2, 26),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 3, 19),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 3, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2021, 4, 2),
        name="Good Friday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2021, 4, 5),
        name="Easter Monday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 4, 16),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 4, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 5, 21),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 5, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 6, 18),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 6, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 7, 16),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 7, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 8, 20),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 8, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 9, 17),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 9, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 10, 15),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 10, 29),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 11, 19),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 11, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 12, 17),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 12, 24),
        name="Christmas Eve",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(14, 5)),
        tags={
            Tags.SPECIAL_CLOSE,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 12, 31),
        name="New Year's Eve",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(14, 5)),
        tags={Tags.SPECIAL_CLOSE, Tags.MONTH_END},
    ),
]

xams_2022 = [
    BusinessCalendarDay(
        date=dt.date(2022, 1, 21),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 1, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 2, 18),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 2, 28),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 3, 18),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 3, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 4, 14),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2022, 4, 15),
        name="Good Friday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2022, 4, 18),
        name="Easter Monday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 4, 29),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 5, 20),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 5, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 6, 17),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 6, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 7, 15),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 7, 29),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 8, 19),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 8, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 9, 16),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 9, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 10, 21),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 10, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 11, 18),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 11, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 12, 16),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    NonBusinessCalendarDay(
        date=dt.date(2022, 12, 26),
        name="Boxing Day",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 12, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
]

xams_2023 = [
    BusinessCalendarDay(
        date=dt.date(2023, 1, 20),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 1, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 2, 17),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 2, 28),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 3, 17),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 3, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2023, 4, 7),
        name="Good Friday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2023, 4, 10),
        name="Easter Monday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 4, 21),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 4, 28),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2023, 5, 1),
        name="Labour Day",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 5, 19),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 5, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 6, 16),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 6, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 7, 21),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 7, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 8, 18),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 8, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 9, 15),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 9, 29),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 10, 20),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 10, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 11, 17),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 11, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 12, 15),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    NonBusinessCalendarDay(
        date=dt.date(2023, 12, 25),
        name="Christmas",
        tags={
            Tags.HOLIDAY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2023, 12, 26),
        name="Boxing Day",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 12, 29),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
]

# XLON: 08:00-16:30
xlon_2021 = [
    NonBusinessCalendarDay(
        date=dt.date(2021, 1, 1),
        name="New Year's Day",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 1, 15),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 1, 29),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 2, 19),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 2, 26),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 3, 19),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 3, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2021, 4, 2),
        name="Good Friday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2021, 4, 5),
        name="Easter Monday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 4, 16),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 4, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2021, 5, 3),
        name="Early May Bank Holiday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 5, 21),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 5, 28),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2021, 5, 31),
        name="Spring Bank Holiday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 6, 18),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 6, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 7, 16),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 7, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 8, 20),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2021, 8, 30),
        name="Summer Bank Holiday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 8, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 9, 17),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 9, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 10, 15),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 10, 29),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 11, 19),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 11, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 12, 17),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 12, 24),
        name="Christmas Eve",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(12, 30)),
        tags={
            Tags.SPECIAL_CLOSE,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2021, 12, 27),
        name="Weekend Christmas",
        tags={
            Tags.HOLIDAY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2021, 12, 28),
        name="Weekend Boxing Day",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 12, 31),
        name="New Year's Eve",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(12, 30)),
        tags={Tags.SPECIAL_CLOSE, Tags.MONTH_END},
    ),
]

xlon_2022 = [
    NonBusinessCalendarDay(
        date=dt.date(2022, 1, 3),
        name="New Year's Day",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 1, 21),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 1, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 2, 18),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 2, 28),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 3, 18),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 3, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 4, 14),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2022, 4, 15),
        name="Good Friday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2022, 4, 18),
        name="Easter Monday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 4, 29),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2022, 5, 2),
        name="Early May Bank Holiday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 5, 20),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 5, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2022, 6, 2),
        name="ad-hoc holiday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2022, 6, 3),
        name="ad-hoc holiday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 6, 17),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 6, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 7, 15),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 7, 29),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 8, 19),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2022, 8, 29),
        name="Summer Bank Holiday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 8, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 9, 16),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    NonBusinessCalendarDay(
        date=dt.date(2022, 9, 19),
        name="ad-hoc holiday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 9, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 10, 21),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 10, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 11, 18),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 11, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 12, 16),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 12, 23),
        name="Christmas Eve",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(12, 30)),
        tags={
            Tags.SPECIAL_CLOSE,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2022, 12, 26),
        name="Boxing Day",
        tags={
            Tags.HOLIDAY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2022, 12, 27),
        name="Weekend Christmas",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 12, 30),
        name="New Year's Eve",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(12, 30)),
        tags={Tags.SPECIAL_CLOSE, Tags.MONTH_END},
    ),
]

xlon_2023 = [
    NonBusinessCalendarDay(
        date=dt.date(2023, 1, 2),
        name="New Year's Day",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 1, 20),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 1, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 2, 17),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 2, 28),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 3, 17),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 3, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2023, 4, 7),
        name="Good Friday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2023, 4, 10),
        name="Easter Monday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 4, 21),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 4, 28),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2023, 5, 1),
        name="Early May Bank Holiday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2023, 5, 8),
        name="ad-hoc holiday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 5, 19),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2023, 5, 29),
        name="Spring Bank Holiday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 5, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 6, 16),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 6, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 7, 21),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 7, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 8, 18),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2023, 8, 28),
        name="Summer Bank Holiday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 8, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 9, 15),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 9, 29),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 10, 20),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 10, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 11, 17),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 11, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 12, 15),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(16, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 12, 22),
        name="Christmas Eve",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(12, 30)),
        tags={
            Tags.SPECIAL_CLOSE,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2023, 12, 25),
        name="Christmas",
        tags={
            Tags.HOLIDAY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2023, 12, 26),
        name="Boxing Day",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 12, 29),
        name="New Year's Eve",
        session=CalendarDaySession(open=dt.time(8, 0), close=dt.time(12, 30)),
        tags={Tags.SPECIAL_CLOSE, Tags.MONTH_END},
    ),
]

# XSWX: 09:00-17:30
xswx_2021 = [
    NonBusinessCalendarDay(
        date=dt.date(2021, 1, 1),
        name="New Year's Day",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 1, 15),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 1, 29),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 2, 19),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 2, 26),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 3, 19),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 3, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2021, 4, 2),
        name="Good Friday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2021, 4, 5),
        name="Easter Monday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 4, 16),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 4, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2021, 5, 13),
        name="Ascension Day",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 5, 21),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2021, 5, 24),
        name="Whit Monday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 5, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 6, 18),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 6, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 7, 16),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 7, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 8, 20),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 8, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 9, 17),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 9, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 10, 15),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 10, 29),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 11, 19),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 11, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 12, 17),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    NonBusinessCalendarDay(
        date=dt.date(2021, 12, 24),
        name="Christmas Eve",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2021, 12, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2021, 12, 31),
        name="New Year's Eve",
        tags={
            Tags.HOLIDAY,
        },
    ),
]

xswx_2022 = [
    BusinessCalendarDay(
        date=dt.date(2022, 1, 21),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 1, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 2, 18),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 2, 28),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 3, 18),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 3, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 4, 14),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2022, 4, 15),
        name="Good Friday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2022, 4, 18),
        name="Easter Monday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 4, 29),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 5, 20),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2022, 5, 26),
        name="Ascension Day",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 5, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2022, 6, 6),
        name="Whit Monday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 6, 17),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 6, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 7, 15),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 7, 29),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2022, 8, 1),
        name="Swiss National Day",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 8, 19),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 8, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 9, 16),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 9, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 10, 21),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 10, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 11, 18),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 11, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 12, 16),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    NonBusinessCalendarDay(
        date=dt.date(2022, 12, 26),
        name="Boxing Day",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2022, 12, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
]

xswx_2023 = [
    NonBusinessCalendarDay(
        date=dt.date(2023, 1, 2),
        name="Berchtold's Day",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 1, 20),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 1, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 2, 17),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 2, 28),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 3, 17),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 3, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2023, 4, 7),
        name="Good Friday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2023, 4, 10),
        name="Easter Monday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 4, 21),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 4, 28),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2023, 5, 1),
        name="Labour Day",
        tags={
            Tags.HOLIDAY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2023, 5, 18),
        name="Ascension Day",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 5, 19),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2023, 5, 29),
        name="Whit Monday",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 5, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 6, 16),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 6, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 7, 21),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 7, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2023, 8, 1),
        name="Swiss National Day",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 8, 18),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 8, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 9, 15),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 9, 29),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 10, 20),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 10, 31),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 11, 17),
        name="monthly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTHLY_EXPIRY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 11, 30),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 12, 15),
        name="quarterly expiry",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={Tags.QUARTERLY_EXPIRY, Tags.MONTHLY_EXPIRY},
    ),
    NonBusinessCalendarDay(
        date=dt.date(2023, 12, 25),
        name="Christmas",
        tags={
            Tags.HOLIDAY,
        },
    ),
    NonBusinessCalendarDay(
        date=dt.date(2023, 12, 26),
        name="Boxing Day",
        tags={
            Tags.HOLIDAY,
        },
    ),
    BusinessCalendarDay(
        date=dt.date(2023, 12, 29),
        name="last trading day of month",
        session=CalendarDaySession(open=dt.time(9, 0), close=dt.time(17, 30)),
        tags={
            Tags.MONTH_END,
        },
    ),
]

# Maps exchange MIC and year to expected special days.
special_days = {
    "XAMS": {
        2021: xams_2021,
        2022: xams_2022,
        2023: xams_2023,
    },
    "XLON": {
        2021: xlon_2021,
        2022: xlon_2022,
        2023: xlon_2023,
    },
    "XSWX": {
        2021: xswx_2021,
        2022: xswx_2022,
        2023: xswx_2023,
    },
}
