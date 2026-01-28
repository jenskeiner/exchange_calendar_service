import logging

import exchange_calendars as ec

from exchange_calendar_service.app.settings import Settings

from .xtae import XTAEExchangeCalendar

log = logging.getLogger(__name__)


def init(settings: Settings):
    log.info("Customizing...")

    # Set logging level to DEBUG.
    logging.basicConfig(level=logging.DEBUG)

    _ = XTAEExchangeCalendar

    # Replace XTAE calendar with custom version.
    ec.calendar_utils.register_calendar_type("XTAE", XTAEExchangeCalendar, force=True)

    # Add completely new calendar.
    ec.calendar_utils.register_calendar_type("FOOO", XTAEExchangeCalendar)

    # Register aliases for exchange calendars, if not already defined.
    _calendar_names = ec.calendar_utils.get_calendar_names(include_aliases=True)

    if (
        settings.exchanges is None or "XNAS" in settings.exchanges.keys()
    ) and "XNAS" not in _calendar_names:
        if "XNYS" in _calendar_names:
            # For Nasdaq mic use XNYS mic.
            ec.calendar_utils.register_calendar_alias("XNAS", "XNYS")
        else:
            raise ValueError("Nasdaq calendar not found.")
    if (
        settings.exchanges is None or "BMEX" in settings.exchanges.keys()
    ) and "BMEX" not in _calendar_names:
        if "XMAD" in _calendar_names:
            # For Madrid, calendar uses segment MIC.
            ec.calendar_utils.register_calendar_alias("BMEX", "XMAD")
        else:
            raise ValueError("Madrid calendar not found.")
