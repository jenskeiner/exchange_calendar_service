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
    def test_get_venues(self, client, test_settings):
        """This test verifies that the GET /v1/mics endpoint returns a list of all available exchange venues."""
        response = client.get("/v1/mics")
        assert response.status_code == HTTPStatus.OK
        assert response.headers["content-type"] == "application/json"
        assert response.json() == [x for x in test_settings.exchanges.keys()]

    def test_get_mic2name(self, client, test_settings):
        """This test verifies that the GET /v1/mic2name endpoint returns a dictionary mapping MICs to venue names."""
        response = client.get("/v1/mic2name")
        assert response.status_code == HTTPStatus.OK
        assert response.headers["content-type"] == "application/json"
        assert response.json() == {x: y for x, y in test_settings.exchanges.items()}

    def test_get_timezones(self, client, test_settings):
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
            {"mic": x, "tz": mic2tz[x]} for x in test_settings.exchanges.keys()
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
            {"mic": x, "tz": mic2standard_time[x]} for x in test_settings.exchanges.keys()
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
    def test_special_days(self, client, test_settings, mic: str, year: int, timezone: str):
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


class TestNextSpecialDays:
    """Tests for /v1/next_special_days endpoint."""

    def test_forward_direction(self, client):
        """Test getting next special days forward from a reference date."""
        response = client.get(
            "/v1/next_special_days",
            params={
                "day": "2024-01-01",
                "forward": True,
                "n": 3,
            },
        )
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert len(data) == 2  # (results, status)
        results, status = data
        assert status == 200
        assert len(results) == 3
        # Dates should be in ascending order
        dates = [r["date"] for r in results]
        assert dates == sorted(dates)

    def test_backward_direction(self, client):
        """Test getting previous special days backward from a reference date."""
        response = client.get(
            "/v1/next_special_days",
            params={
                "day": "2024-12-31",
                "forward": False,
                "n": 3,
            },
        )
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        results, status = data
        assert status == 200
        assert len(results) == 3
        # Dates should be in descending order
        dates = [r["date"] for r in results]
        assert dates == sorted(dates, reverse=True)

    def test_inclusive_true(self, client):
        """Test that inclusive=True includes the reference day if it's a special day."""
        # 2024-12-25 is Christmas (a holiday)
        response = client.get(
            "/v1/next_special_days",
            params={
                "day": "2024-12-25",
                "inclusive": True,
                "forward": True,
                "n": 1,
            },
        )
        assert response.status_code == HTTPStatus.OK
        results, _ = response.json()
        assert len(results) >= 1
        # First result should be on or after 2024-12-25
        assert results[0]["date"] >= "2024-12-25"

    def test_inclusive_false(self, client):
        """Test that inclusive=False excludes the reference day."""
        response = client.get(
            "/v1/next_special_days",
            params={
                "day": "2024-12-25",
                "inclusive": False,
                "forward": True,
                "n": 1,
            },
        )
        assert response.status_code == HTTPStatus.OK
        results, _ = response.json()
        # Results should be after 2024-12-25
        for r in results:
            assert r["date"] > "2024-12-25"

    def test_with_range_limiting(self, client):
        """Test that range parameter limits the search window."""
        response = client.get(
            "/v1/next_special_days",
            params={
                "day": "2024-06-01",
                "forward": True,
                "n": 10,
                "range": 30,  # Only search within 30 days
            },
        )
        assert response.status_code == HTTPStatus.OK
        results, status = response.json()
        # All results should be within 30 days of 2024-06-01
        for r in results:
            from datetime import datetime, timedelta

            ref = datetime.fromisoformat("2024-06-01").date()
            result_date = datetime.fromisoformat(r["date"]).date()
            assert result_date <= ref + timedelta(days=30)

    def test_single_mic_filter(self, client):
        """Test filtering results to a single MIC."""
        response = client.get(
            "/v1/next_special_days",
            params={
                "day": "2024-01-01",
                "forward": True,
                "n": 2,
                "mic": "XLON",
            },
        )
        assert response.status_code == HTTPStatus.OK
        results, _ = response.json()
        # All results should only include XLON
        for r in results:
            for c in r["classifications"]:
                assert "XLON" in c["mics"]
                assert len(c["mics"]) == 1

    def test_multiple_mic_filter(self, client):
        """Test filtering results to multiple MICs."""
        response = client.get(
            "/v1/next_special_days",
            params={
                "day": "2024-01-01",
                "forward": True,
                "n": 2,
                "mic": ["XLON", "XAMS"],
            },
        )
        assert response.status_code == HTTPStatus.OK
        results, _ = response.json()
        # Results should only include XLON and XAMS
        for r in results:
            for c in r["classifications"]:
                for mic in c["mics"]:
                    assert mic in ["XLON", "XAMS"]

    def test_year_boundary_forward(self, client):
        """Test searching forward across year boundaries."""
        # Use a date late in the year and request many days to ensure year boundary crossing
        response = client.get(
            "/v1/next_special_days",
            params={
                "day": "2024-12-01",
                "forward": True,
                "n": 50,  # Request many to find days in next year
            },
        )
        assert response.status_code == HTTPStatus.OK
        results, status = response.json()
        # Should find days in 2025 (calendar has quarterly expiries throughout year)
        dates = [r["date"] for r in results]
        # At least some results should be in 2025 (quarterly expiries happen quarterly)
        assert len([d for d in dates if d.startswith("2025")]) > 0

    def test_year_boundary_backward(self, client):
        """Test searching backward across year boundaries."""
        response = client.get(
            "/v1/next_special_days",
            params={
                "day": "2024-01-10",
                "forward": False,
                "n": 5,
            },
        )
        assert response.status_code == HTTPStatus.OK
        results, status = response.json()
        # Should find days in 2023
        dates = [r["date"] for r in results]
        assert any(d.startswith("2023") for d in dates)

    def test_exclude_tags_forward(self, client):
        """Test that exclude_tags parameter filters out tagged dates when searching forward."""
        from exchange_calendar_service.core.common.context import Context

        # Set up a tagged date - 2024-12-24 is before a holiday
        mic = "XLON"
        tagged_date = "2024-12-24"
        test_tag = "exclude-test-tag"

        response = client.post(
            "/update",
            json={mic: {"meta": {tagged_date: {"tags": [test_tag]}}}},
            headers={"X-API-KEY": "test"},
        )
        assert response.status_code == HTTPStatus.OK

        # Refresh cache
        Context().cache.refresh(mic)

        try:
            # Get special days without exclude_tags
            response = client.get(
                "/v1/next_special_days",
                params={
                    "day": "2024-12-20",
                    "forward": True,
                    "n": 10,
                    "mic": mic,
                },
            )
            assert response.status_code == HTTPStatus.OK
            results_without_filter, _ = response.json()
            dates_without_filter = [r["date"] for r in results_without_filter]

            # Get special days with exclude_tags
            response = client.get(
                "/v1/next_special_days",
                params=[
                    ('day', '2024-12-20'),
                    ('forward', True),
                    ('n', 10),
                    ('mic', mic),
                    ('exclude_tags', test_tag),
                ],
            )
            assert response.status_code == HTTPStatus.OK
            results_with_filter, _ = response.json()
            dates_with_filter = [r["date"] for r in results_with_filter]

            # The tagged date should be in results without filter but not with filter
            if tagged_date in dates_without_filter:
                assert tagged_date not in dates_with_filter

        finally:
            # Clean up - remove the tag
            client.post(
                "/update",
                json={mic: {"meta": {tagged_date: {"tags": []}}}},
                headers={"X-API-KEY": "test"},
            )
            Context().cache.refresh(mic)

    def test_exclude_tags_backward(self, client):
        """Test that exclude_tags parameter filters out tagged dates when searching backward."""
        from exchange_calendar_service.core.common.context import Context

        mic = "XLON"
        tagged_date = "2024-12-27"
        test_tag = "backward-exclude-tag"

        response = client.post(
            "/update",
            json={mic: {"meta": {tagged_date: {"tags": [test_tag]}}}},
            headers={"X-API-KEY": "test"},
        )
        assert response.status_code == HTTPStatus.OK

        Context().cache.refresh(mic)

        try:
            # Get special days without exclude_tags
            response = client.get(
                "/v1/next_special_days",
                params={
                    "day": "2024-12-31",
                    "forward": False,
                    "n": 10,
                    "mic": mic,
                },
            )
            assert response.status_code == HTTPStatus.OK
            results_without_filter, _ = response.json()
            dates_without_filter = [r["date"] for r in results_without_filter]

            # Get special days with exclude_tags
            response = client.get(
                "/v1/next_special_days",
                params=[
                    ('day', '2024-12-31'),
                    ('forward', False),
                    ('n', 10),
                    ('mic', mic),
                    ('exclude_tags', test_tag),
                ],
            )
            assert response.status_code == HTTPStatus.OK
            results_with_filter, _ = response.json()
            dates_with_filter = [r["date"] for r in results_with_filter]

            # The tagged date should be filtered out
            if tagged_date in dates_without_filter:
                assert tagged_date not in dates_with_filter

        finally:
            # Clean up
            client.post(
                "/update",
                json={mic: {"meta": {tagged_date: {"tags": []}}}},
                headers={"X-API-KEY": "test"},
            )
            Context().cache.refresh(mic)

    def test_exclude_tags_multiple(self, client):
        """Test that multiple exclude_tags filter out dates with any of the tags."""
        from exchange_calendar_service.core.common.context import Context

        mic = "XAMS"
        tag1 = "exclude-tag-1"
        tag2 = "exclude-tag-2"
        date1 = "2024-03-28"
        date2 = "2024-03-29"

        # Add tags to two different dates
        response = client.post(
            "/update",
            json={
                mic: {
                    "meta": {
                        date1: {"tags": [tag1]},
                        date2: {"tags": [tag2]},
                    }
                }
            },
            headers={"X-API-KEY": "test"},
        )
        assert response.status_code == HTTPStatus.OK

        Context().cache.refresh(mic)

        try:
            # Get special days with both tags excluded
            response = client.get(
                "/v1/next_special_days",
                params=[
                    ('day', '2024-03-25'),
                    ('forward', True),
                    ('n', 10),
                    ('mic', mic),
                    ('exclude_tags', tag1),
                    ('exclude_tags', tag2),
                ],
            )
            assert response.status_code == HTTPStatus.OK
            results, _ = response.json()
            dates = [r["date"] for r in results]

            # Neither tagged date should be in results
            assert date1 not in dates
            assert date2 not in dates

        finally:
            # Clean up
            client.post(
                "/update",
                json={
                    mic: {
                        "meta": {
                            date1: {"tags": []},
                            date2: {"tags": []},
                        }
                    }
                },
                headers={"X-API-KEY": "test"},
            )
            Context().cache.refresh(mic)


class TestNextBusinessDays:
    """Tests for /v1/next_business_days endpoint."""

    def test_forward_business_days(self, client):
        """Test getting next business days forward from a reference date."""
        response = client.get(
            "/v1/next_business_days",
            params={
                "day": "2024-01-01",
                "forward": True,
                "n": 5,
            },
        )
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        results, status = data
        assert status == 200
        assert len(results) == 5
        # All results should be business days (is_business_day=True)
        for r in results:
            for c in r["classifications"]:
                assert c["is_business_day"] is True

    def test_backward_business_days(self, client):
        """Test getting previous business days backward from a reference date."""
        response = client.get(
            "/v1/next_business_days",
            params={
                "day": "2024-12-31",
                "forward": False,
                "n": 5,
            },
        )
        assert response.status_code == HTTPStatus.OK
        results, status = response.json()
        assert status == 200
        assert len(results) == 5
        # Dates should be in descending order
        dates = [r["date"] for r in results]
        assert dates == sorted(dates, reverse=True)

    def test_business_days_include_regular(self, client):
        """Test that business days endpoint includes regular trading days."""
        response = client.get(
            "/v1/next_business_days",
            params={
                "day": "2024-01-15",  # A Monday
                "forward": True,
                "n": 10,
            },
        )
        assert response.status_code == HTTPStatus.OK
        results, _ = response.json()
        # Should include regular business days
        has_regular = any(
            any(c["type"] == "regular" for c in r["classifications"])
            for r in results
        )
        assert has_regular

    def test_business_days_with_range(self, client):
        """Test range limiting with business days."""
        response = client.get(
            "/v1/next_business_days",
            params={
                "day": "2024-06-01",
                "forward": True,
                "n": 20,
                "range": 10,  # Only 10 days range
            },
        )
        assert response.status_code == HTTPStatus.OK
        results, status = response.json()
        # Results limited by range
        from datetime import datetime, timedelta

        ref = datetime.fromisoformat("2024-06-01").date()
        for r in results:
            result_date = datetime.fromisoformat(r["date"]).date()
            assert result_date <= ref + timedelta(days=10)

    def test_range_exceeded_status(self, client):
        """Test that searching beyond allowed range returns 416 status."""
        response = client.get(
            "/v1/next_business_days",
            params={
                "day": "2024-01-01",
                "forward": True,
                "n": 10000,  # Request more days than available in range
            },
        )
        assert response.status_code == HTTPStatus.OK
        results, status = response.json()
        # Status should be 416 when range is exceeded
        assert status == 416

    def test_exclude_tags_business_days(self, client):
        """Test that exclude_tags parameter filters out tagged business days."""
        from exchange_calendar_service.core.common.context import Context

        mic = "XSWX"
        # Tag a business day (not a weekend or holiday)
        tagged_date = "2024-03-20"
        test_tag = "business-exclude-tag"

        response = client.post(
            "/update",
            json={mic: {"meta": {tagged_date: {"tags": [test_tag]}}}},
            headers={"X-API-KEY": "test"},
        )
        assert response.status_code == HTTPStatus.OK

        Context().cache.refresh(mic)

        try:
            # Get business days without exclude_tags
            response = client.get(
                "/v1/next_business_days",
                params={
                    "day": "2024-03-18",
                    "forward": True,
                    "n": 5,
                    "mic": mic,
                },
            )
            assert response.status_code == HTTPStatus.OK
            results_without_filter, _ = response.json()
            dates_without_filter = [r["date"] for r in results_without_filter]

            # Get business days with exclude_tags
            response = client.get(
                "/v1/next_business_days",
                params=[
                    ('day', '2024-03-18'),
                    ('forward', True),
                    ('n', 5),
                    ('mic', mic),
                    ('exclude_tags', test_tag),
                ],
            )
            assert response.status_code == HTTPStatus.OK
            results_with_filter, _ = response.json()
            dates_with_filter = [r["date"] for r in results_with_filter]

            # The tagged date should be filtered out
            if tagged_date in dates_without_filter:
                assert tagged_date not in dates_with_filter

        finally:
            # Clean up
            client.post(
                "/update",
                json={mic: {"meta": {tagged_date: {"tags": []}}}},
                headers={"X-API-KEY": "test"},
            )
            Context().cache.refresh(mic)

    def test_exclude_tags_backward_business_days(self, client):
        """Test that exclude_tags filters when searching backward for business days."""
        from exchange_calendar_service.core.common.context import Context

        mic = "XLON"
        tagged_date = "2024-11-28"
        test_tag = "backward-business-exclude"

        response = client.post(
            "/update",
            json={mic: {"meta": {tagged_date: {"tags": [test_tag]}}}},
            headers={"X-API-KEY": "test"},
        )
        assert response.status_code == HTTPStatus.OK

        Context().cache.refresh(mic)

        try:
            # Get business days backward with exclude_tags
            response = client.get(
                "/v1/next_business_days",
                params=[
                    ('day', '2024-11-29'),
                    ('forward', False),
                    ('n', 5),
                    ('mic', mic),
                    ('exclude_tags', test_tag),
                ],
            )
            assert response.status_code == HTTPStatus.OK
            results, _ = response.json()
            dates = [r["date"] for r in results]

            # The tagged date should not be in results
            assert tagged_date not in dates

        finally:
            # Clean up
            client.post(
                "/update",
                json={mic: {"meta": {tagged_date: {"tags": []}}}},
                headers={"X-API-KEY": "test"},
            )
            Context().cache.refresh(mic)
