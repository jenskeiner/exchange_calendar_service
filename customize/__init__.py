import exchange_calendars as ec

from exchange_calendar_service.app.settings import Settings

# A custom version of the XTAE exchange calendar, where Sundays were always non-business days.
from .xtae import XTAEExchangeCalendar


def init(settings: Settings):
    """Apply customizations to exchange calendars."""

    # Replace standard XTAE calendar with custom version.
    ec.calendar_utils.register_calendar_type("XTAE", XTAEExchangeCalendar, force=True)

    # Add the same calendar under a new fake MIC.
    ec.calendar_utils.register_calendar_type("FOOO", XTAEExchangeCalendar)

    # Register additional aliases for some calendars.

    _calendar_names = ec.calendar_utils.get_calendar_names(include_aliases=True)

    # Add XNAS -> XNYS, maybe.
    if (
        settings.exchanges is None or "XNAS" in settings.exchanges
    ) and "XNAS" not in _calendar_names:
        if "XNYS" in _calendar_names:
            ec.calendar_utils.register_calendar_alias("XNAS", "XNYS")
        else:
            raise ValueError("Nasdaq calendar not found.")

    # Add BMEX -> XMAD, maybe.
    if (
        settings.exchanges is None or "BMEX" in settings.exchanges
    ) and "BMEX" not in _calendar_names:
        if "XMAD" in _calendar_names:
            ec.calendar_utils.register_calendar_alias("BMEX", "XMAD")
        else:
            raise ValueError("Madrid calendar not found.")
