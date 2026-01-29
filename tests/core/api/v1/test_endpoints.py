import datetime as dt
from http import HTTPStatus
from zoneinfo import ZoneInfo

import pytest
from pydantic import TypeAdapter

from exchange_calendar_service.app.api.v1.endpoints import (
    DayClassification,
    SpecialOpenCloseDayClassification,
)

from .special_days import special_days


@pytest.mark.usefixtures("client")
class TestVenues:
    def test_get_venues(self, client, settings):
        """This test verifies that the GET /v1/mics endpoint returns a list of all available exchange venues."""
        response = client.get("/v1/mics")
        assert response.status_code == HTTPStatus.OK
        assert response.headers["content-type"] == "application/json"
        assert response.json() == [x for x in settings.exchanges.keys()]

    def test_get_mic2name(self, client, settings):
        """This test verifies that the GET /v1/mic2name endpoint returns a dictionary mapping MICs to venue names."""
        response = client.get("/v1/mic2name")
        assert response.status_code == HTTPStatus.OK
        assert response.headers["content-type"] == "application/json"
        assert response.json() == {x: y for x, y in settings.exchanges.items()}

    def test_get_timezones(self, client, settings):
        """This test verifies that the GET /v1/timezones endpoint returns the correct timezone or standard time for
        each exchange.
        """

        # Maps exchange MIC to expected standard time.
        mic2tz = {
            "XAMS": "CET",
            "XLON": "WET",
            "XSWX": "CET",
        }

        # Get standard times for all exchanges.
        response = client.get("/v1/timezone", params={"standardise": True})

        assert response.status_code == HTTPStatus.OK
        assert response.headers["content-type"] == "application/json"
        assert response.json() == [
            {"mic": x, "tz": mic2tz[x]} for x in settings.exchanges.keys()
        ]

        # Get standard time for one exchange.
        mic = "XLON"
        response = client.get("/v1/timezone", params={"mic": mic, "standardise": True})

        assert response.status_code == HTTPStatus.OK
        assert response.headers["content-type"] == "application/json"
        assert response.json() == [{"mic": mic, "tz": mic2tz[mic]}]

        # Maps exchange MIC to expected timezone.
        mic2standard_time = {
            "XAMS": "Europe/Amsterdam",
            "XLON": "Europe/London",
            "XSWX": "Europe/Zurich",
        }

        # Get timezones for all exchanges.
        response = client.get("/v1/timezone", params={"standardise": False})

        assert response.status_code == HTTPStatus.OK
        assert response.headers["content-type"] == "application/json"
        assert response.json() == [
            {"mic": x, "tz": mic2standard_time[x]} for x in settings.exchanges.keys()
        ]

        # Get timezone for one exchange.
        mic = "XLON"
        response = client.get("/v1/timezone", params={"mic": mic, "standardise": False})

        assert response.status_code == HTTPStatus.OK
        assert response.headers["content-type"] == "application/json"
        assert response.json() == [{"mic": mic, "tz": mic2standard_time[mic]}]


ta = TypeAdapter(list[DayClassification])


class TestSpecialDays:
    @pytest.mark.parametrize(
        "timezone", [None, "CET", "Europe/Berlin", "Europe/London"]
    )
    @pytest.mark.parametrize("year", [2021, 2022, 2023])
    @pytest.mark.parametrize("mic", ["XAMS", "XLON", "XSWX"])
    def test_special_days(self, client, settings, mic: str, year: int, timezone: str):
        """This test verifies that the POST /v1/special_days endpoint returns the correct special days for each
        exchange.
        """

        # Get expected special days for exchange and year.
        expected = special_days[mic][year]

        # Convert times to given timezone, maybe.
        if timezone is not None:
            tz = ZoneInfo(timezone)

            def convert(c: DayClassification):
                if isinstance(c, SpecialOpenCloseDayClassification):
                    return SpecialOpenCloseDayClassification.model_validate(
                        {
                            **c.model_dump(),
                            "time": dt.datetime.combine(c.date, c.time)
                            .replace(tzinfo=ZoneInfo(c.tz))
                            .astimezone(tz)
                            .time(),
                            "tz": str(tz),
                        }
                    )
                else:
                    return c

            expected = list(map(convert, expected))

        # Set up request parameters.
        params = {"mic": mic, "year": year}

        # Add timezone parameter, if given.
        if timezone is not None:
            params["tz"] = timezone

        response = client.get("/v1/special_days", params=params)
        assert response.status_code == HTTPStatus.OK
        assert response.headers["content-type"] == "application/json"
        assert ta.validate_json(response.text) == expected
