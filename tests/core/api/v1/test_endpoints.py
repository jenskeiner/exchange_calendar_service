import datetime as dt
import json
from http import HTTPStatus
from pathlib import Path

import pytest

from exchange_calendar_service.app.api.v1.endpoints import (
    Tags,
)


@pytest.mark.usefixtures("client")
class TestReferenceData:
    def test_get_exchanges(self, client, test_settings):
        """This test verifies that the GET /v1/exchanges endpoint returns a list of all available MICs."""
        response = client.get("/v1/exchanges")
        assert response.status_code == HTTPStatus.OK
        assert response.headers["content-type"] == "application/json"
        assert response.json() == [x for x in test_settings.exchanges]

    @pytest.mark.parametrize(
        "mic,expected_tz",
        [
            ("XAMS", "Europe/Amsterdam"),
            ("XLON", "Europe/London"),
            ("XSWX", "Europe/Zurich"),
            ("BVMF", "America/Sao_Paulo"),
        ],
    )
    def test_get_exchange_info(self, client, mic, expected_tz):
        """This test verifies that the GET /v1/exchanges/{mic} endpoint returns exchange info."""
        response = client.get(f"/v1/exchanges/{mic}")
        assert response.status_code == HTTPStatus.OK
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert data["mic"] == mic
        assert data["tz"] == expected_tz


# Load ground truth data.
_ground_truth_path = Path(__file__).parent / "ground_truth.json"
with open(_ground_truth_path) as f:
    _ground_truth = json.load(f)


def _assert_days_equal(actual: list[dict], expected: list[dict]) -> None:
    """Compare two lists of day objects, ignoring tag order."""
    assert len(actual) == len(expected)
    for a, e in zip(actual, expected):
        assert a.keys() == e.keys()
        assert a["date"] == e["date"]
        assert a["business_day"] == e["business_day"]
        if "name" in e:
            assert a["name"] == e["name"]
        # Tags are sets - order doesn't matter
        assert set(a["tags"]) == set(e["tags"])
        if "session" in e:
            assert a["session"] == e["session"]


def _filter_days(
    days: list[dict],
    business_day: bool | None = None,
    include_tags: set[str] | None = None,
    exclude_tags: set[str] | None = None,
) -> list[dict]:
    """Filter list of days by criteria matching the endpoint behavior."""
    result = days
    if business_day is not None:
        result = [d for d in result if d["business_day"] == business_day]
    if include_tags is not None:
        result = [d for d in result if include_tags.issubset(set(d["tags"]))]
    if exclude_tags is not None:
        result = [d for d in result if not exclude_tags.intersection(d["tags"])]
    return result


@pytest.mark.usefixtures("client")
class TestListExchangeDays:
    """Tests for GET /v1/exchanges/{mic}/days endpoint."""

    @pytest.mark.parametrize("mic", ["XAMS", "XLON", "XSWX", "BVMF"])
    @pytest.mark.parametrize("year", [2021, 2022, 2023])
    def test_all_days(self, client, mic: str, year: int):
        """Test getting all days in a year."""
        start = dt.date(year, 1, 1)
        end = dt.date(year, 12, 31)
        expected = _ground_truth[mic][str(year)]

        params = {"start": start.isoformat(), "end": end.isoformat()}
        response = client.get(f"/v1/exchanges/{mic}/days", params=params)

        assert response.status_code == HTTPStatus.OK
        assert response.headers["content-type"] == "application/json"
        _assert_days_equal(response.json(), expected)

    @pytest.mark.parametrize("mic", ["XAMS", "XLON", "XSWX", "BVMF"])
    @pytest.mark.parametrize("year", [2021, 2022, 2023])
    def test_business_day_filter(self, client, mic: str, year: int):
        """Test filtering by business_day=True."""
        start = dt.date(year, 1, 1)
        end = dt.date(year, 12, 31)
        all_days = _ground_truth[mic][str(year)]
        expected = _filter_days(all_days, business_day=True)

        params = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "business_day": True,
        }
        response = client.get(f"/v1/exchanges/{mic}/days", params=params)

        assert response.status_code == HTTPStatus.OK
        _assert_days_equal(response.json(), expected)

    @pytest.mark.parametrize("mic", ["XAMS", "XLON", "XSWX", "BVMF"])
    @pytest.mark.parametrize("year", [2021, 2022, 2023])
    def test_non_business_day_filter(self, client, mic: str, year: int):
        """Test filtering by business_day=False (holidays and weekends)."""
        start = dt.date(year, 1, 1)
        end = dt.date(year, 12, 31)
        all_days = _ground_truth[mic][str(year)]
        expected = _filter_days(all_days, business_day=False)

        params = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "business_day": False,
        }
        response = client.get(f"/v1/exchanges/{mic}/days", params=params)

        assert response.status_code == HTTPStatus.OK
        _assert_days_equal(response.json(), expected)

    @pytest.mark.parametrize("mic", ["XAMS", "XLON", "XSWX", "BVMF"])
    @pytest.mark.parametrize("year", [2021, 2022, 2023])
    def test_include_tags_special_open(self, client, mic: str, year: int):
        """Test filtering by include_tags=special open."""
        start = dt.date(year, 1, 1)
        end = dt.date(year, 12, 31)
        all_days = _ground_truth[mic][str(year)]
        expected = _filter_days(all_days, include_tags={Tags.SPECIAL_OPEN.value})

        params = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "include_tags": Tags.SPECIAL_OPEN.value,
        }
        response = client.get(f"/v1/exchanges/{mic}/days", params=params)

        assert response.status_code == HTTPStatus.OK
        _assert_days_equal(response.json(), expected)

    @pytest.mark.parametrize("mic", ["XAMS", "XLON", "XSWX", "BVMF"])
    @pytest.mark.parametrize("year", [2021, 2022, 2023])
    def test_include_tags_special_close(self, client, mic: str, year: int):
        """Test filtering by include_tags=special close."""
        start = dt.date(year, 1, 1)
        end = dt.date(year, 12, 31)
        all_days = _ground_truth[mic][str(year)]
        expected = _filter_days(all_days, include_tags={Tags.SPECIAL_CLOSE.value})

        params = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "include_tags": Tags.SPECIAL_CLOSE.value,
        }
        response = client.get(f"/v1/exchanges/{mic}/days", params=params)

        assert response.status_code == HTTPStatus.OK
        _assert_days_equal(response.json(), expected)

    @pytest.mark.parametrize("mic", ["XAMS", "XLON", "XSWX", "BVMF"])
    @pytest.mark.parametrize("year", [2021, 2022, 2023])
    def test_include_tags_quarterly_expiry(self, client, mic: str, year: int):
        """Test filtering by include_tags=quarterly expiry."""
        start = dt.date(year, 1, 1)
        end = dt.date(year, 12, 31)
        all_days = _ground_truth[mic][str(year)]
        expected = _filter_days(all_days, include_tags={Tags.QUARTERLY_EXPIRY.value})

        params = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "include_tags": Tags.QUARTERLY_EXPIRY.value,
        }
        response = client.get(f"/v1/exchanges/{mic}/days", params=params)

        assert response.status_code == HTTPStatus.OK
        _assert_days_equal(response.json(), expected)

    @pytest.mark.parametrize("mic", ["XAMS", "XLON", "XSWX", "BVMF"])
    @pytest.mark.parametrize("year", [2021, 2022, 2023])
    def test_include_tags_monthly_expiry(self, client, mic: str, year: int):
        """Test filtering by include_tags=monthly expiry."""
        start = dt.date(year, 1, 1)
        end = dt.date(year, 12, 31)
        all_days = _ground_truth[mic][str(year)]
        expected = _filter_days(all_days, include_tags={Tags.MONTHLY_EXPIRY.value})

        params = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "include_tags": Tags.MONTHLY_EXPIRY.value,
        }
        response = client.get(f"/v1/exchanges/{mic}/days", params=params)

        assert response.status_code == HTTPStatus.OK
        _assert_days_equal(response.json(), expected)

    @pytest.mark.parametrize("mic", ["XAMS", "XLON", "XSWX", "BVMF"])
    @pytest.mark.parametrize("year", [2021, 2022, 2023])
    def test_include_tags_month_end(self, client, mic: str, year: int):
        """Test filtering by include_tags=month end."""
        start = dt.date(year, 1, 1)
        end = dt.date(year, 12, 31)
        all_days = _ground_truth[mic][str(year)]
        expected = _filter_days(all_days, include_tags={Tags.MONTH_END.value})

        params = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "include_tags": Tags.MONTH_END.value,
        }
        response = client.get(f"/v1/exchanges/{mic}/days", params=params)

        assert response.status_code == HTTPStatus.OK
        _assert_days_equal(response.json(), expected)

    @pytest.mark.parametrize("mic", ["XAMS", "XLON", "XSWX", "BVMF"])
    @pytest.mark.parametrize("year", [2021, 2022, 2023])
    def test_include_tags_weekend(self, client, mic: str, year: int):
        """Test filtering by include_tags=weekend."""
        start = dt.date(year, 1, 1)
        end = dt.date(year, 12, 31)
        all_days = _ground_truth[mic][str(year)]
        expected = _filter_days(all_days, include_tags={Tags.WEEKEND.value})

        params = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "include_tags": Tags.WEEKEND.value,
        }
        response = client.get(f"/v1/exchanges/{mic}/days", params=params)

        assert response.status_code == HTTPStatus.OK
        _assert_days_equal(response.json(), expected)

    @pytest.mark.parametrize("mic", ["XAMS", "XLON", "XSWX", "BVMF"])
    @pytest.mark.parametrize("year", [2021, 2022, 2023])
    def test_include_tags_regular(self, client, mic: str, year: int):
        """Test filtering by include_tags=regular."""
        start = dt.date(year, 1, 1)
        end = dt.date(year, 12, 31)
        all_days = _ground_truth[mic][str(year)]
        expected = _filter_days(all_days, include_tags={Tags.REGULAR.value})

        params = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "include_tags": Tags.REGULAR.value,
        }
        response = client.get(f"/v1/exchanges/{mic}/days", params=params)

        assert response.status_code == HTTPStatus.OK
        _assert_days_equal(response.json(), expected)

    @pytest.mark.parametrize("mic", ["XAMS", "XLON", "XSWX"])
    def test_limit(self, client, mic: str):
        """Test limit parameter."""
        start = dt.date(2021, 1, 1)
        end = dt.date(2021, 12, 31)

        params = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "limit": 10,
        }
        response = client.get(f"/v1/exchanges/{mic}/days", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert len(result) == 10

    @pytest.mark.parametrize(
        "order,expected_first,expected_last",
        [
            ("asc", "2021-01-01", "2021-01-10"),
            ("desc", "2021-12-31", "2021-12-22"),
        ],
    )
    def test_order(self, client, order: str, expected_first: str, expected_last: str):
        """Test order parameter (asc/desc)."""
        mic = "XAMS"
        start = dt.date(2021, 1, 1)
        end = dt.date(2021, 12, 31)

        params = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "limit": 10,
            "order": order,
        }
        response = client.get(f"/v1/exchanges/{mic}/days", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert len(result) == 10
        assert result[0]["date"] == expected_first
        assert result[-1]["date"] == expected_last

    @pytest.mark.parametrize(
        "order,limit,expected_dates",
        [
            (
                "asc",
                5,
                ["2021-01-01", "2021-01-02", "2021-01-03", "2021-01-04", "2021-01-05"],
            ),
            (
                "desc",
                5,
                ["2021-12-31", "2021-12-30", "2021-12-29", "2021-12-28", "2021-12-27"],
            ),
        ],
    )
    def test_limit_and_order_combined(
        self, client, order: str, limit: int, expected_dates: list[str]
    ):
        """Test limit and order parameters combined."""
        mic = "XLON"
        start = dt.date(2021, 1, 1)
        end = dt.date(2021, 12, 31)

        params = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "order": order,
            "limit": limit,
        }
        response = client.get(f"/v1/exchanges/{mic}/days", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert [d["date"] for d in result] == expected_dates

    @pytest.mark.parametrize("mic", ["XAMS", "XLON", "XSWX"])
    def test_date_range_single_day(self, client, mic: str):
        """Test getting a single day."""
        single_day = dt.date(2021, 6, 15)

        params = {
            "start": single_day.isoformat(),
            "end": single_day.isoformat(),
        }
        response = client.get(f"/v1/exchanges/{mic}/days", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert len(result) == 1
        assert result[0]["date"] == "2021-06-15"

    @pytest.mark.parametrize("mic", ["XAMS", "XLON", "XSWX"])
    def test_date_range_partial_year(self, client, mic: str):
        """Test getting a partial date range."""
        start = dt.date(2021, 6, 1)
        end = dt.date(2021, 6, 30)

        params = {
            "start": start.isoformat(),
            "end": end.isoformat(),
        }
        response = client.get(f"/v1/exchanges/{mic}/days", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # All dates should be in June 2021
        for day in result:
            assert day["date"].startswith("2021-06")
        # Should have 30 days
        assert len(result) == 30

    def test_multiple_include_tags_and_logic(self, client):
        """Test filtering with multiple include_tags (AND logic)."""
        # XAMS 2021-05-01 has both 'weekend' and 'holiday' tags
        mic = "XAMS"
        start = dt.date(2021, 5, 1)
        end = dt.date(2021, 5, 1)

        # Get days with weekend tag only
        params_weekend = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "include_tags": Tags.WEEKEND.value,
        }
        response_weekend = client.get(
            f"/v1/exchanges/{mic}/days", params=params_weekend
        )
        days_weekend = {d["date"] for d in response_weekend.json()}

        # Get days with holiday tag only
        params_holiday = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "include_tags": Tags.HOLIDAY.value,
        }
        response_holiday = client.get(
            f"/v1/exchanges/{mic}/days", params=params_holiday
        )
        days_holiday = {d["date"] for d in response_holiday.json()}

        # Get days with both tags (should be intersection)
        params_both = [
            ("start", start.isoformat()),
            ("end", end.isoformat()),
            ("include_tags", Tags.WEEKEND.value),
            ("include_tags", Tags.HOLIDAY.value),
        ]
        response_both = client.get(f"/v1/exchanges/{mic}/days", params=params_both)
        days_both = {d["date"] for d in response_both.json()}

        # Individual queries should find this day
        assert "2021-05-01" in days_weekend
        assert "2021-05-01" in days_holiday

        # Result with both tags should be intersection (only days with BOTH tags)
        assert days_both == days_weekend & days_holiday
        assert "2021-05-01" in days_both

    @pytest.mark.parametrize("exclude_tags", [Tags.WEEKEND.value, Tags.REGULAR.value])
    def test_exclude_tags(self, client, exclude_tags: str):
        """Test exclude_tags parameter."""
        mic = "XSWX"
        start = dt.date(2021, 1, 1)
        end = dt.date(2021, 12, 31)

        # Get all days
        params_all = {
            "start": start.isoformat(),
            "end": end.isoformat(),
        }
        response_all = client.get(f"/v1/exchanges/{mic}/days", params=params_all)
        all_dates = {d["date"] for d in response_all.json()}

        # Get days without excluded tag
        params_exclude = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "exclude_tags": exclude_tags,
        }
        response_exclude = client.get(
            f"/v1/exchanges/{mic}/days", params=params_exclude
        )
        excluded_dates = {d["date"] for d in response_exclude.json()}

        # Excluded dates should be subset of all dates
        assert excluded_dates.issubset(all_dates)
        # Should have fewer results
        assert len(excluded_dates) < len(all_dates)

    def test_business_day_and_include_tags_combined(self, client):
        """Test combining business_day filter with include_tags."""
        mic = "XAMS"
        start = dt.date(2021, 1, 1)
        end = dt.date(2021, 12, 31)

        params = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "business_day": True,
            "include_tags": Tags.MONTH_END.value,
        }
        response = client.get(f"/v1/exchanges/{mic}/days", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # All results should be business days with month end tag
        for day in result:
            assert day["business_day"] is True
            assert Tags.MONTH_END.value in day["tags"]


@pytest.mark.usefixtures("client")
class TestGetExchangeDay:
    """Tests for GET /v1/exchanges/{mic}/days/{day} endpoint."""

    @pytest.mark.parametrize(
        "mic,day,expected_business_day,expected_tags,expected_name",
        [
            # Regular business days
            ("XAMS", "2021-01-04", True, {Tags.REGULAR.value}, None),
            ("XLON", "2021-02-01", True, {Tags.REGULAR.value}, None),
            ("XSWX", "2021-03-01", True, {Tags.REGULAR.value}, None),
            ("BVMF", "2021-01-04", True, {Tags.REGULAR.value}, None),
            # Holidays
            ("XAMS", "2021-01-01", False, {Tags.HOLIDAY.value}, "New Year's Day"),
            ("XLON", "2021-12-27", False, {Tags.HOLIDAY.value}, "Weekend Christmas"),
            ("XSWX", "2021-12-24", False, {Tags.HOLIDAY.value}, "Christmas Eve"),
            (
                "BVMF",
                "2021-01-01",
                False,
                {Tags.HOLIDAY.value},
                "Dia da Confraternizacao Universal",
            ),
            # Weekend days
            ("XAMS", "2021-01-02", False, {Tags.WEEKEND.value}, None),
            ("XLON", "2021-01-03", False, {Tags.WEEKEND.value}, None),
            ("XSWX", "2021-01-09", False, {Tags.WEEKEND.value}, None),
            # Month end
            (
                "XAMS",
                "2021-01-29",
                True,
                {Tags.REGULAR.value, Tags.MONTH_END.value},
                None,
            ),
            (
                "XLON",
                "2021-03-31",
                True,
                {Tags.REGULAR.value, Tags.MONTH_END.value},
                None,
            ),
            (
                "XSWX",
                "2021-06-30",
                True,
                {Tags.REGULAR.value, Tags.MONTH_END.value},
                None,
            ),
            # Quarterly expiry
            (
                "XAMS",
                "2021-03-19",
                True,
                {
                    Tags.REGULAR.value,
                    Tags.QUARTERLY_EXPIRY.value,
                    Tags.MONTHLY_EXPIRY.value,
                },
                None,
            ),
            (
                "XLON",
                "2021-06-18",
                True,
                {
                    Tags.REGULAR.value,
                    Tags.QUARTERLY_EXPIRY.value,
                    Tags.MONTHLY_EXPIRY.value,
                },
                None,
            ),
            (
                "XSWX",
                "2021-09-17",
                True,
                {
                    Tags.REGULAR.value,
                    Tags.QUARTERLY_EXPIRY.value,
                    Tags.MONTHLY_EXPIRY.value,
                },
                None,
            ),
            # Month end (non-expiry)
            (
                "XAMS",
                "2021-01-29",
                True,
                {Tags.REGULAR.value, Tags.MONTH_END.value},
                None,
            ),
            (
                "XLON",
                "2021-01-29",
                True,
                {Tags.REGULAR.value, Tags.MONTH_END.value},
                None,
            ),
            (
                "XSWX",
                "2021-01-29",
                True,
                {Tags.REGULAR.value, Tags.MONTH_END.value},
                None,
            ),
        ],
    )
    def test_get_exchange_day(
        self,
        client,
        mic: str,
        day: str,
        expected_business_day: bool,
        expected_tags: set[str],
        expected_name: str | None,
    ):
        """Test getting a single day with various characteristics."""
        response = client.get(f"/v1/exchanges/{mic}/days/{day}")

        assert response.status_code == HTTPStatus.OK
        assert response.headers["content-type"] == "application/json"
        result = response.json()

        assert result["date"] == day
        assert result["business_day"] == expected_business_day
        assert set(result["tags"]) == expected_tags
        if expected_name is not None:
            assert result["name"] == expected_name

        if expected_business_day:
            assert "session" in result
            assert "open" in result["session"]
            assert "close" in result["session"]

    @pytest.mark.parametrize(
        "mic,day,expected_open,expected_close,expected_tags,expected_name",
        [
            # Special close days
            (
                "XAMS",
                "2021-12-24",
                "09:00:00",
                "14:05:00",
                {Tags.SPECIAL_CLOSE.value},
                "Christmas Eve",
            ),
            (
                "XLON",
                "2021-12-24",
                "08:00:00",
                "12:30:00",
                {Tags.SPECIAL_CLOSE.value},
                "Christmas Eve",
            ),
            # Special open days
            (
                "BVMF",
                "2021-02-17",
                "13:00:00",
                "18:00:00",
                {Tags.SPECIAL_OPEN.value},
                "Quarta Cinzas",
            ),
            # Days with session times
            ("XSWX", "2021-01-04", "09:00:00", "17:30:00", {Tags.REGULAR.value}, None),
        ],
    )
    def test_get_exchange_day_session_times(
        self,
        client,
        mic: str,
        day: str,
        expected_open: str,
        expected_close: str,
        expected_tags: set[str],
        expected_name: str | None,
    ):
        """Test that session times are correctly returned for business days."""
        response = client.get(f"/v1/exchanges/{mic}/days/{day}")

        assert response.status_code == HTTPStatus.OK
        result = response.json()

        assert result["business_day"] is True
        assert result["session"]["open"] == expected_open
        assert result["session"]["close"] == expected_close
        assert set(result["tags"]) == expected_tags
        if expected_name is not None:
            assert result["name"] == expected_name

    @pytest.mark.parametrize(
        "mic,day",
        [
            ("XAMS", "2021-01-04"),
            ("XLON", "2021-06-15"),
            ("XSWX", "2021-09-20"),
            ("BVMF", "2021-03-15"),
        ],
    )
    def test_get_exchange_day_response_structure(self, client, mic: str, day: str):
        """Test that the response structure is valid for various exchanges."""
        response = client.get(f"/v1/exchanges/{mic}/days/{day}")

        assert response.status_code == HTTPStatus.OK
        result = response.json()

        # Verify all expected fields are present
        assert "date" in result
        assert "tags" in result
        assert "business_day" in result

        # Verify types
        assert isinstance(result["date"], str)
        assert isinstance(result["tags"], list)
        assert isinstance(result["business_day"], bool)


@pytest.mark.usefixtures("client")
class TestSerializationKeyOrder:
    """Tests that JSON keys are returned in the canonical order: date, name, business_day, session, tags."""

    _CANONICAL_ORDER = ("date", "name", "business_day", "session", "tags")

    @staticmethod
    def _expected_order(keys: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(k for k in TestSerializationKeyOrder._CANONICAL_ORDER if k in keys)

    @pytest.mark.parametrize(
        "mic,day",
        [
            ("XAMS", "2021-01-04"),
            ("XLON", "2021-06-18"),
            ("XSWX", "2021-12-24"),
            ("BVMF", "2021-02-17"),
        ],
    )
    def test_single_business_day_key_order(self, client, mic: str, day: str):
        """Verify key order for a single business day response."""
        response = client.get(f"/v1/exchanges/{mic}/days/{day}")
        assert response.status_code == HTTPStatus.OK
        pairs = json.loads(response.text, object_pairs_hook=lambda p: p)
        keys = tuple(k for k, _ in pairs)
        assert keys == self._expected_order(keys)

    @pytest.mark.parametrize(
        "mic,day",
        [
            ("XAMS", "2021-01-01"),
            ("XAMS", "2021-01-02"),
            ("XLON", "2021-12-27"),
            ("XSWX", "2021-01-09"),
        ],
    )
    def test_single_non_business_day_key_order(self, client, mic: str, day: str):
        """Verify key order for a single non-business day response (no session key)."""
        response = client.get(f"/v1/exchanges/{mic}/days/{day}")
        assert response.status_code == HTTPStatus.OK
        pairs = json.loads(response.text, object_pairs_hook=lambda p: p)
        keys = tuple(k for k, _ in pairs)
        assert keys == self._expected_order(keys)
        assert "session" not in keys


@pytest.mark.usefixtures("client")
class TestListNextExchangeDays:
    """Tests for GET /v1/exchanges/{mic}/days/{day}/next endpoint."""

    @pytest.mark.parametrize(
        "direction,order,expected_first,expected_last",
        [
            # forward + asc: natural asc, no reversal. inclusive=True by default, so includes start date
            ("forward", "asc", "2021-06-15", "2021-06-24"),
            # forward + desc: natural asc, then reversed
            ("forward", "desc", "2021-06-24", "2021-06-15"),
            # backward + desc: natural desc, no reversal. includes start date at beginning
            ("backward", "desc", "2021-06-15", "2021-06-06"),
            # backward + asc: natural desc, then reversed
            ("backward", "asc", "2021-06-06", "2021-06-15"),
        ],
    )
    def test_ordering_logic(
        self, client, direction, order, expected_first, expected_last
    ):
        """Test all 4 ordering combinations to verify correct ordering logic.

        Key insight:
        - forward: order0="asc" (natural order from start), then reversed if order != "asc"
        - backward: order0="desc" (natural order from start), then reversed if order != "desc"
        - inclusive=True by default, so start date is included
        """
        mic = "XAMS"
        day = dt.date(2021, 6, 15)
        limit = 10

        params = {
            "direction": direction,
            "order": order,
            "limit": limit,
        }
        response = client.get(
            f"/v1/exchanges/{mic}/days/{day.isoformat()}/next", params=params
        )

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert len(result) == 10
        assert result[0]["date"] == expected_first
        assert result[-1]["date"] == expected_last

    @pytest.mark.parametrize(
        "direction,order,expected_dates",
        [
            # forward + asc: dates in ascending order from start date (inclusive by default)
            (
                "forward",
                "asc",
                ["2021-06-15", "2021-06-16", "2021-06-17", "2021-06-18", "2021-06-21"],
            ),
            # forward + desc: same dates but in descending order
            (
                "forward",
                "desc",
                ["2021-06-21", "2021-06-18", "2021-06-17", "2021-06-16", "2021-06-15"],
            ),
            # backward + desc: dates in descending order from start date (inclusive by default)
            (
                "backward",
                "desc",
                ["2021-06-15", "2021-06-14", "2021-06-11", "2021-06-10", "2021-06-09"],
            ),
            # backward + asc: same dates but in ascending order
            (
                "backward",
                "asc",
                ["2021-06-09", "2021-06-10", "2021-06-11", "2021-06-14", "2021-06-15"],
            ),
        ],
    )
    def test_ordering_with_business_days_only(
        self, client, direction, order, expected_dates
    ):
        """Test ordering with business_day filter, which produces non-contiguous dates.

        This tests the key ordering logic: the endpoint first collects days in the natural
        order for the search direction, then re-sorts if the requested order differs.
        """
        mic = "XSWX"
        day = dt.date(2021, 6, 15)
        limit = 5

        params = {
            "direction": direction,
            "order": order,
            "business_day": True,
            "limit": limit,
        }
        response = client.get(
            f"/v1/exchanges/{mic}/days/{day.isoformat()}/next", params=params
        )

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert [d["date"] for d in result] == expected_dates

    @pytest.mark.parametrize(
        "direction,order,inclusive,expected_dates",
        [
            # forward + asc, inclusive: includes start date
            (
                "forward",
                "asc",
                True,
                ["2021-06-15", "2021-06-16", "2021-06-17", "2021-06-18"],
            ),
            # forward + asc, exclusive: excludes start date
            (
                "forward",
                "asc",
                False,
                ["2021-06-16", "2021-06-17", "2021-06-18", "2021-06-21"],
            ),
            # backward + desc, inclusive: includes start date
            (
                "backward",
                "desc",
                True,
                ["2021-06-15", "2021-06-14", "2021-06-11", "2021-06-10"],
            ),
            # backward + desc, exclusive: excludes start date
            (
                "backward",
                "desc",
                False,
                ["2021-06-14", "2021-06-11", "2021-06-10", "2021-06-09"],
            ),
        ],
    )
    def test_inclusive_parameter(
        self, client, direction, order, inclusive, expected_dates
    ):
        """Test inclusive parameter with both directions."""
        mic = "XSWX"
        day = dt.date(2021, 6, 15)
        limit = 4

        params = {
            "direction": direction,
            "order": order,
            "inclusive": inclusive,
            "business_day": True,
            "limit": limit,
        }
        response = client.get(
            f"/v1/exchanges/{mic}/days/{day.isoformat()}/next", params=params
        )

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert [d["date"] for d in result] == expected_dates

    @pytest.mark.parametrize(
        "mic,day,direction,expected_first_date",
        [
            # From a non-business day (Saturday), forward should find next business day
            ("XAMS", dt.date(2021, 6, 12), "forward", "2021-06-14"),
            # From a non-business day (Saturday), backward should find previous business day
            ("XAMS", dt.date(2021, 6, 12), "backward", "2021-06-11"),
            # From a holiday, forward should find next business day
            ("XAMS", dt.date(2021, 4, 2), "forward", "2021-04-06"),
            # From a holiday, backward should find previous business day
            ("XAMS", dt.date(2021, 4, 2), "backward", "2021-04-01"),
        ],
    )
    def test_from_non_business_day(
        self, client, mic, day, direction, expected_first_date
    ):
        """Test searching from a non-business day."""
        limit = 1

        params = {
            "direction": direction,
            "business_day": True,
            "limit": limit,
        }
        response = client.get(
            f"/v1/exchanges/{mic}/days/{day.isoformat()}/next", params=params
        )

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert len(result) == 1
        assert result[0]["date"] == expected_first_date
        assert result[0]["business_day"] is True

    @pytest.mark.parametrize(
        "direction,limit,expected_first_date",
        [
            ("forward", 5, "2021-06-15"),  # includes start date by default
            ("backward", 5, "2021-06-09"),  # includes start date by default
        ],
    )
    def test_limit_parameter(self, client, direction, limit, expected_first_date):
        """Test limit parameter with both directions."""
        mic = "XSWX"
        day = dt.date(2021, 6, 15)

        params = {
            "direction": direction,
            "business_day": True,
            "limit": limit,
        }
        response = client.get(
            f"/v1/exchanges/{mic}/days/{day.isoformat()}/next", params=params
        )

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert len(result) == limit
        assert result[0]["date"] == expected_first_date

    def test_end_parameter_forward(self, client):
        """Test end parameter limits forward search range."""
        mic = "XAMS"
        day = dt.date(2021, 6, 15)
        end = dt.date(2021, 6, 18)

        params = {
            "direction": "forward",
            "end": end.isoformat(),
            "limit": 100,
        }
        response = client.get(
            f"/v1/exchanges/{mic}/days/{day.isoformat()}/next", params=params
        )

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # Should only include dates up to and including 2021-06-18
        for d in result:
            assert d["date"] <= "2021-06-18"
        # Verify last result is exactly the end date
        assert result[-1]["date"] == "2021-06-18"

    def test_end_parameter_backward(self, client):
        """Test end parameter limits backward search range.

        For backward direction, 'end' serves as the lower bound of the search.
        Results are returned in the requested order (default desc for backward).
        """
        mic = "XAMS"
        day = dt.date(2021, 6, 15)
        end = dt.date(2021, 6, 10)

        params = {
            "direction": "backward",
            "end": end.isoformat(),
            "limit": 100,
        }
        response = client.get(
            f"/v1/exchanges/{mic}/days/{day.isoformat()}/next", params=params
        )

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # Should only include dates from end date onwards
        for d in result:
            assert d["date"] >= "2021-06-10"
        # Verify first result (earliest date) is the end date
        assert result[0]["date"] == "2021-06-10"
        # Verify last result includes the start day
        assert result[-1]["date"] == "2021-06-15"

    @pytest.mark.parametrize(
        "direction,include_tags,expected_tags_in_result",
        [
            ("forward", [Tags.MONTH_END.value], Tags.MONTH_END.value),
            ("backward", [Tags.MONTH_END.value], Tags.MONTH_END.value),
            ("forward", [Tags.HOLIDAY.value], Tags.HOLIDAY.value),
            ("backward", [Tags.HOLIDAY.value], Tags.HOLIDAY.value),
        ],
    )
    def test_include_tags(
        self, client, direction, include_tags, expected_tags_in_result
    ):
        """Test include_tags parameter with both directions."""
        mic = "XAMS"
        day = dt.date(2021, 6, 1)
        limit = 3

        params = [
            ("direction", direction),
            ("limit", limit),
        ]
        for tag in include_tags:
            params.append(("include_tags", tag))

        response = client.get(
            f"/v1/exchanges/{mic}/days/{day.isoformat()}/next", params=params
        )

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # All results should have the expected tag
        for d in result:
            assert expected_tags_in_result in d["tags"]

    @pytest.mark.parametrize(
        "direction,exclude_tags,forbidden_tag",
        [
            ("forward", [Tags.WEEKEND.value], Tags.WEEKEND.value),
            ("backward", [Tags.WEEKEND.value], Tags.WEEKEND.value),
        ],
    )
    def test_exclude_tags(self, client, direction, exclude_tags, forbidden_tag):
        """Test exclude_tags parameter with both directions."""
        mic = "XLON"
        day = dt.date(2021, 6, 15)

        params = [
            ("direction", direction),
            ("limit", 20),
        ]
        for tag in exclude_tags:
            params.append(("exclude_tags", tag))

        response = client.get(
            f"/v1/exchanges/{mic}/days/{day.isoformat()}/next", params=params
        )

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # No results should have the excluded tag
        for d in result:
            assert forbidden_tag not in d["tags"]

    @pytest.mark.parametrize(
        "direction,business_day,expected_business_day_value",
        [
            ("forward", True, True),
            ("forward", False, False),
            ("backward", True, True),
            ("backward", False, False),
        ],
    )
    def test_business_day_filter(
        self, client, direction, business_day, expected_business_day_value
    ):
        """Test business_day filter with both directions."""
        mic = "XSWX"
        day = dt.date(2021, 6, 15)
        limit = 5

        params = {
            "direction": direction,
            "business_day": business_day,
            "limit": limit,
        }
        response = client.get(
            f"/v1/exchanges/{mic}/days/{day.isoformat()}/next", params=params
        )

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # All results should match the business_day filter
        for d in result:
            assert d["business_day"] == expected_business_day_value

    @pytest.mark.parametrize(
        "mic,day,direction,business_day,include_tags,end",
        [
            # Find next month ends from start of June - need to limit with end date
            (
                "XAMS",
                dt.date(2021, 6, 1),
                "forward",
                True,
                Tags.MONTH_END.value,
                dt.date(2021, 8, 31),
            ),
            # Find previous month ends from end of June - need to limit with end date
            (
                "XAMS",
                dt.date(2021, 6, 30),
                "backward",
                True,
                Tags.MONTH_END.value,
                dt.date(2021, 2, 1),
            ),
        ],
    )
    def test_combined_filters(
        self, client, mic, day, direction, business_day, include_tags, end
    ):
        """Test combining business_day filter with include_tags."""
        limit = 10

        params = [
            ("direction", direction),
            ("business_day", business_day),
            ("include_tags", include_tags),
            ("end", end.isoformat()),
            ("limit", limit),
        ]
        response = client.get(
            f"/v1/exchanges/{mic}/days/{day.isoformat()}/next", params=params
        )

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # All results should be business days with the expected tag
        for d in result:
            assert d["business_day"] is True
            assert include_tags in d["tags"]
        # Verify we got some results
        assert len(result) > 0

    def test_empty_result(self, client):
        """Test that empty result is returned when search range is empty.

        Use the end parameter to create an empty search range.
        """
        mic = "XSWX"
        day = dt.date(2021, 6, 15)
        # Set end before start day with direction=forward to create empty range
        end = dt.date(2021, 6, 10)

        params = {
            "direction": "forward",
            "end": end.isoformat(),
            "limit": 10,
        }
        response = client.get(
            f"/v1/exchanges/{mic}/days/{day.isoformat()}/next", params=params
        )

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert len(result) == 0

    @pytest.mark.parametrize(
        "mic,day,direction,order",
        [
            ("XAMS", dt.date(2021, 1, 1), "forward", "asc"),
            ("XLON", dt.date(2021, 12, 31), "backward", "desc"),
        ],
    )
    def test_single_result(self, client, mic, day, direction, order):
        """Test scenarios that return exactly one result."""
        limit = 1

        params = {
            "direction": direction,
            "order": order,
            "limit": limit,
            "business_day": True,
        }
        response = client.get(
            f"/v1/exchanges/{mic}/days/{day.isoformat()}/next", params=params
        )

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert len(result) == 1
        assert "date" in result[0]
        assert "business_day" in result[0]

    def test_forward_asc_from_holiday_with_tags(self, client):
        """Test forward asc from a holiday, looking for business days with month end tag."""
        mic = "XAMS"
        # Good Friday is a holiday
        day = dt.date(2021, 4, 2)

        params = [
            ("direction", "forward"),
            ("order", "asc"),
            ("business_day", True),
            ("include_tags", Tags.MONTH_END.value),
            ("limit", 3),
        ]
        response = client.get(
            f"/v1/exchanges/{mic}/days/{day.isoformat()}/next", params=params
        )

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # Should find month ends after Good Friday: Apr 30, May 31, Jun 30
        assert len(result) == 3
        assert result[0]["date"] == "2021-04-30"
        assert result[1]["date"] == "2021-05-31"
        assert result[2]["date"] == "2021-06-30"

    def test_backward_desc_from_holiday_with_tags(self, client):
        """Test backward desc from a holiday, looking for business days with month end tag."""
        mic = "XLON"
        # Spring Bank Holiday is a holiday
        day = dt.date(2021, 5, 31)

        params = [
            ("direction", "backward"),
            ("order", "desc"),
            ("business_day", True),
            ("include_tags", Tags.MONTH_END.value),
            ("limit", 3),
        ]
        response = client.get(
            f"/v1/exchanges/{mic}/days/{day.isoformat()}/next", params=params
        )

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # Should find month ends before May 31 in desc order: May 28, Apr 30, Mar 31
        assert len(result) == 3
        assert result[0]["date"] == "2021-05-28"
        assert result[1]["date"] == "2021-04-30"
        assert result[2]["date"] == "2021-03-31"


@pytest.mark.usefixtures("client")
class TestListDaysMultiExchange:
    """Tests for GET /v1/days endpoint (multi-exchange)."""

    def test_two_exchanges_basic(self, client):
        """Test basic query with two exchanges."""
        start = dt.date(2021, 6, 14)
        end = dt.date(2021, 6, 16)

        params = [
            ("start", start.isoformat()),
            ("end", end.isoformat()),
            ("mics", "XLON"),
            ("mics", "XSWX"),
        ]
        response = client.get("/v1/days", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # Should have 3 dates
        assert len(result) == 3
        # Each result should have both XLON and XSWX
        for day_entry in result:
            assert "XLON" in day_entry
            assert "XSWX" in day_entry
            # Both exchanges should have the same date
            assert day_entry["XLON"]["date"] == day_entry["XSWX"]["date"]
            # MICs should be in alphabetical order
            assert list(day_entry.keys()) == ["XLON", "XSWX"]

    def test_three_exchanges(self, client):
        """Test query with three exchanges."""
        start = dt.date(2021, 6, 15)
        end = dt.date(2021, 6, 15)

        params = [
            ("start", start.isoformat()),
            ("end", end.isoformat()),
            ("mics", "XAMS"),
            ("mics", "XLON"),
            ("mics", "XSWX"),
        ]
        response = client.get("/v1/days", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert len(result) == 1
        # Should have all three exchanges in alphabetical order
        assert list(result[0].keys()) == ["XAMS", "XLON", "XSWX"]

    def test_business_day_filter(self, client):
        """Test filtering by business_day=True across multiple exchanges."""
        start = dt.date(2021, 6, 14)
        end = dt.date(2021, 6, 20)

        params = [
            ("start", start.isoformat()),
            ("end", end.isoformat()),
            ("mics", "XLON"),
            ("mics", "XSWX"),
            ("business_day", True),
        ]
        response = client.get("/v1/days", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # All results should have business_day=True for both exchanges
        for day_entry in result:
            for mic_data in day_entry.values():
                assert mic_data["business_day"] is True

    def test_non_business_day_filter(self, client):
        """Test filtering by business_day=False across multiple exchanges."""
        start = dt.date(2021, 6, 12)
        end = dt.date(2021, 6, 13)

        params = [
            ("start", start.isoformat()),
            ("end", end.isoformat()),
            ("mics", "XLON"),
            ("mics", "XSWX"),
            ("business_day", False),
        ]
        response = client.get("/v1/days", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # Should have weekend days
        assert len(result) == 2
        # All results should have business_day=False
        for day_entry in result:
            for mic_data in day_entry.values():
                assert mic_data["business_day"] is False
                assert Tags.WEEKEND.value in mic_data["tags"]

    def test_limit_parameter(self, client):
        """Test limit parameter on grouped results."""
        start = dt.date(2021, 6, 14)
        end = dt.date(2021, 6, 25)

        params = [
            ("start", start.isoformat()),
            ("end", end.isoformat()),
            ("mics", "XLON"),
            ("mics", "XSWX"),
            ("limit", 5),
        ]
        response = client.get("/v1/days", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # Should have exactly 5 date records
        assert len(result) == 5

    def test_order_asc(self, client):
        """Test ascending order."""
        start = dt.date(2021, 6, 14)
        end = dt.date(2021, 6, 16)

        params = [
            ("start", start.isoformat()),
            ("end", end.isoformat()),
            ("mics", "XLON"),
            ("mics", "XSWX"),
            ("order", "asc"),
        ]
        response = client.get("/v1/days", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        dates = [list(entry.values())[0]["date"] for entry in result]
        assert dates == ["2021-06-14", "2021-06-15", "2021-06-16"]

    def test_order_desc(self, client):
        """Test descending order."""
        start = dt.date(2021, 6, 14)
        end = dt.date(2021, 6, 16)

        params = [
            ("start", start.isoformat()),
            ("end", end.isoformat()),
            ("mics", "XLON"),
            ("mics", "XSWX"),
            ("order", "desc"),
        ]
        response = client.get("/v1/days", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        dates = [list(entry.values())[0]["date"] for entry in result]
        assert dates == ["2021-06-16", "2021-06-15", "2021-06-14"]

    def test_include_tags(self, client):
        """Test filtering by include_tags."""
        start = dt.date(2021, 3, 1)
        end = dt.date(2021, 3, 31)

        params = [
            ("start", start.isoformat()),
            ("end", end.isoformat()),
            ("mics", "XLON"),
            ("mics", "XSWX"),
            ("include_tags", Tags.QUARTERLY_EXPIRY.value),
        ]
        response = client.get("/v1/days", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # All results should have quarterly_expiry tag
        for day_entry in result:
            for mic_data in day_entry.values():
                assert Tags.QUARTERLY_EXPIRY.value in mic_data["tags"]

    def test_exclude_tags(self, client):
        """Test filtering by exclude_tags."""
        start = dt.date(2021, 1, 1)
        end = dt.date(2021, 12, 31)

        params = [
            ("start", start.isoformat()),
            ("end", end.isoformat()),
            ("mics", "XAMS"),
            ("mics", "XLON"),
            ("exclude_tags", Tags.WEEKEND.value),
        ]
        response = client.get("/v1/days", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # No results should have weekend tag
        for day_entry in result:
            for mic_data in day_entry.values():
                assert Tags.WEEKEND.value not in mic_data["tags"]

    def test_mics_alphabetical_order(self, client):
        """Test that MICs within each date entry are in alphabetical order."""
        start = dt.date(2021, 6, 15)
        end = dt.date(2021, 6, 15)

        # Pass MICs in non-alphabetical order
        params = [
            ("start", start.isoformat()),
            ("end", end.isoformat()),
            ("mics", "XSWX"),
            ("mics", "XAMS"),
            ("mics", "XLON"),
        ]
        response = client.get("/v1/days", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # MICs should be in alphabetical order regardless of input order
        assert list(result[0].keys()) == ["XAMS", "XLON", "XSWX"]

    def test_different_timezones(self, client):
        """Test querying exchanges in different timezones."""
        start = dt.date(2021, 6, 15)
        end = dt.date(2021, 6, 15)

        params = [
            ("start", start.isoformat()),
            ("end", end.isoformat()),
            ("mics", "XLON"),  # Europe/London
            ("mics", "BVMF"),  # America/Sao_Paulo
            ("mics", "XSWX"),  # Europe/Zurich
        ]
        response = client.get("/v1/days", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert len(result) == 1
        # All three exchanges should be present
        assert "BVMF" in result[0]
        assert "XLON" in result[0]
        assert "XSWX" in result[0]

    def test_single_mic(self, client):
        """Test that single MIC works like the single-exchange endpoint but with grouped response."""
        start = dt.date(2021, 6, 14)
        end = dt.date(2021, 6, 16)

        params = [
            ("start", start.isoformat()),
            ("end", end.isoformat()),
            ("mics", "XLON"),
        ]
        response = client.get("/v1/days", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert len(result) == 3
        # Each entry should have only XLON
        for day_entry in result:
            assert list(day_entry.keys()) == ["XLON"]
            assert "XLON" in day_entry

    def test_empty_result(self, client):
        """Test that empty result is returned when no days match filters."""
        start = dt.date(2021, 6, 15)
        end = dt.date(2021, 6, 15)

        params = [
            ("start", start.isoformat()),
            ("end", end.isoformat()),
            ("mics", "XLON"),
            ("mics", "XSWX"),
            ("business_day", False),
            ("include_tags", Tags.QUARTERLY_EXPIRY.value),  # Business days only
        ]
        response = client.get("/v1/days", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # Quarterly expiry days are business days, so this should return empty
        assert len(result) == 0

    def test_combined_filters(self, client):
        """Test combining multiple filters."""
        start = dt.date(2021, 12, 1)
        end = dt.date(2021, 12, 31)

        params = [
            ("start", start.isoformat()),
            ("end", end.isoformat()),
            ("mics", "XLON"),
            ("mics", "XSWX"),
            ("business_day", True),
            ("include_tags", Tags.MONTH_END.value),
            ("order", "asc"),
        ]
        response = client.get("/v1/days", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # All results should be business days with month end tag
        for day_entry in result:
            for mic_data in day_entry.values():
                assert mic_data["business_day"] is True
                assert Tags.MONTH_END.value in mic_data["tags"]


@pytest.mark.usefixtures("client")
class TestGetDayMultiExchange:
    """Tests for GET /v1/days/{day} endpoint (multi-exchange)."""

    def test_two_exchanges_business_day(self, client):
        """Test getting a business day for two exchanges."""
        day = "2021-06-15"

        params = [
            ("mics", "XLON"),
            ("mics", "XSWX"),
        ]
        response = client.get(f"/v1/days/{day}", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # Should have both exchanges
        assert "XLON" in result
        assert "XSWX" in result
        # Both should be business days
        assert result["XLON"]["business_day"] is True
        assert result["XSWX"]["business_day"] is True
        # Both should have the same date
        assert result["XLON"]["date"] == day
        assert result["XSWX"]["date"] == day
        # MICs should be in alphabetical order
        assert list(result.keys()) == ["XLON", "XSWX"]

    def test_three_exchanges(self, client):
        """Test getting a day for three exchanges."""
        day = "2021-06-15"

        params = [
            ("mics", "XAMS"),
            ("mics", "XLON"),
            ("mics", "XSWX"),
        ]
        response = client.get(f"/v1/days/{day}", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # Should have all three exchanges in alphabetical order
        assert list(result.keys()) == ["XAMS", "XLON", "XSWX"]

    def test_holiday(self, client):
        """Test getting a holiday for multiple exchanges."""
        day = "2021-12-25"  # Christmas

        params = [
            ("mics", "XLON"),
            ("mics", "XSWX"),
        ]
        response = client.get(f"/v1/days/{day}", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # Both should be holidays
        assert result["XLON"]["business_day"] is False
        assert result["XSWX"]["business_day"] is False
        assert Tags.HOLIDAY.value in result["XLON"]["tags"]
        assert Tags.HOLIDAY.value in result["XSWX"]["tags"]

    def test_single_exchange(self, client):
        """Test getting a day for a single exchange."""
        day = "2021-06-15"

        params = [("mics", "XLON")]
        response = client.get(f"/v1/days/{day}", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert list(result.keys()) == ["XLON"]
        assert result["XLON"]["date"] == day

    def test_weekend(self, client):
        """Test getting a weekend day for multiple exchanges."""
        day = "2021-06-12"  # Saturday

        params = [
            ("mics", "XAMS"),
            ("mics", "XLON"),
        ]
        response = client.get(f"/v1/days/{day}", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # Both should be weekends
        assert result["XAMS"]["business_day"] is False
        assert result["XLON"]["business_day"] is False
        assert Tags.WEEKEND.value in result["XAMS"]["tags"]
        assert Tags.WEEKEND.value in result["XLON"]["tags"]

    def test_mics_alphabetical_order(self, client):
        """Test that MICs are in alphabetical order regardless of input order."""
        day = "2021-06-15"

        # Pass MICs in non-alphabetical order
        params = [
            ("mics", "XSWX"),
            ("mics", "XAMS"),
            ("mics", "XLON"),
        ]
        response = client.get(f"/v1/days/{day}", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # MICs should be in alphabetical order
        assert list(result.keys()) == ["XAMS", "XLON", "XSWX"]


@pytest.mark.usefixtures("client")
class TestListNextDaysMultiExchange:
    """Tests for GET /v1/days/{day}/next endpoint (multi-exchange)."""

    def test_forward_two_exchanges(self, client):
        """Test forward search with two exchanges."""
        day = dt.date(2021, 6, 15)

        params = [
            ("mics", "XLON"),
            ("mics", "XSWX"),
            ("direction", "forward"),
            ("limit", 5),
        ]
        response = client.get(f"/v1/days/{day.isoformat()}/next", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # Should have 5 date records
        assert len(result) == 5
        # Each result should have both exchanges
        for day_entry in result:
            assert "XLON" in day_entry
            assert "XSWX" in day_entry
            # Both exchanges should have the same date
            assert day_entry["XLON"]["date"] == day_entry["XSWX"]["date"]

    def test_backward_two_exchanges(self, client):
        """Test backward search with two exchanges."""
        day = dt.date(2021, 6, 15)

        params = [
            ("mics", "XLON"),
            ("mics", "XSWX"),
            ("direction", "backward"),
            ("limit", 5),
        ]
        response = client.get(f"/v1/days/{day.isoformat()}/next", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # Should have 5 date records
        assert len(result) == 5
        # Each result should have both exchanges
        for day_entry in result:
            assert "XLON" in day_entry
            assert "XSWX" in day_entry

    @pytest.mark.parametrize(
        "direction,order,expected_first",
        [
            # forward + asc: natural asc order, first is start date
            ("forward", "asc", "2021-06-15"),
            # forward + desc: natural asc (limited to 1), then reversed (still just 1)
            ("forward", "desc", "2021-06-15"),
            # backward + desc: natural desc order, first is start date
            ("backward", "desc", "2021-06-15"),
            # backward + asc: natural desc (limited to 1), then reversed (still just 1)
            ("backward", "asc", "2021-06-15"),
        ],
    )
    def test_ordering_logic(self, client, direction, order, expected_first):
        """Test all 4 ordering combinations."""
        day = dt.date(2021, 6, 15)
        limit = 1

        params = [
            ("mics", "XLON"),
            ("mics", "XSWX"),
            ("direction", direction),
            ("order", order),
            ("limit", limit),
        ]
        response = client.get(f"/v1/days/{day.isoformat()}/next", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert len(result) == 1
        # Check the date from the first exchange
        assert list(result[0].values())[0]["date"] == expected_first

    def test_inclusive_false(self, client):
        """Test exclusive search (day not included)."""
        day = dt.date(2021, 6, 15)

        params = [
            ("mics", "XLON"),
            ("mics", "XSWX"),
            ("direction", "forward"),
            ("inclusive", False),
            ("limit", 3),
        ]
        response = client.get(f"/v1/days/{day.isoformat()}/next", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert len(result) == 3
        # First result should be the day after (excluding weekends, so June 16 is Wednesday)
        assert list(result[0].values())[0]["date"] == "2021-06-16"

    def test_business_day_filter(self, client):
        """Test with business_day filter."""
        day = dt.date(2021, 6, 15)

        params = [
            ("mics", "XLON"),
            ("mics", "XSWX"),
            ("direction", "forward"),
            ("business_day", True),
            ("limit", 5),
        ]
        response = client.get(f"/v1/days/{day.isoformat()}/next", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # All results should be business days
        for day_entry in result:
            for mic_data in day_entry.values():
                assert mic_data["business_day"] is True

    def test_include_tags(self, client):
        """Test with include_tags filter."""
        day = dt.date(2021, 3, 1)

        params = [
            ("mics", "XLON"),
            ("mics", "XSWX"),
            ("direction", "forward"),
            ("include_tags", Tags.QUARTERLY_EXPIRY.value),
            ("limit", 3),
        ]
        response = client.get(f"/v1/days/{day.isoformat()}/next", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # All results should have quarterly_expiry tag
        for day_entry in result:
            for mic_data in day_entry.values():
                assert Tags.QUARTERLY_EXPIRY.value in mic_data["tags"]

    def test_end_parameter_forward(self, client):
        """Test end parameter limits forward search range."""
        day = dt.date(2021, 6, 15)
        end = dt.date(2021, 6, 18)

        params = [
            ("mics", "XLON"),
            ("mics", "XSWX"),
            ("direction", "forward"),
            ("end", end.isoformat()),
            ("limit", 100),
        ]
        response = client.get(f"/v1/days/{day.isoformat()}/next", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # Should only include dates up to and including 2021-06-18
        for day_entry in result:
            for mic_data in day_entry.values():
                assert mic_data["date"] <= "2021-06-18"

    def test_end_parameter_backward(self, client):
        """Test end parameter limits backward search range."""
        day = dt.date(2021, 6, 15)
        end = dt.date(2021, 6, 10)

        params = [
            ("mics", "XLON"),
            ("mics", "XSWX"),
            ("direction", "backward"),
            ("end", end.isoformat()),
            ("limit", 100),
        ]
        response = client.get(f"/v1/days/{day.isoformat()}/next", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # Should only include dates from end date onwards
        for day_entry in result:
            for mic_data in day_entry.values():
                assert mic_data["date"] >= "2021-06-10"

    def test_three_exchanges(self, client):
        """Test with three exchanges."""
        day = dt.date(2021, 6, 15)

        params = [
            ("mics", "XAMS"),
            ("mics", "XLON"),
            ("mics", "XSWX"),
            ("direction", "forward"),
            ("limit", 3),
        ]
        response = client.get(f"/v1/days/{day.isoformat()}/next", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert len(result) == 3
        # Each result should have all three exchanges in alphabetical order
        for day_entry in result:
            assert list(day_entry.keys()) == ["XAMS", "XLON", "XSWX"]

    def test_mics_alphabetical_order(self, client):
        """Test that MICs within each date entry are in alphabetical order."""
        day = dt.date(2021, 6, 15)

        # Pass MICs in non-alphabetical order
        params = [
            ("mics", "XSWX"),
            ("mics", "XAMS"),
            ("mics", "XLON"),
            ("direction", "forward"),
            ("limit", 1),
        ]
        response = client.get(f"/v1/days/{day.isoformat()}/next", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # MICs should be in alphabetical order regardless of input order
        assert list(result[0].keys()) == ["XAMS", "XLON", "XSWX"]


@pytest.mark.usefixtures("client")
class TestListInstants:
    """Tests for GET /v1/instants endpoint."""

    def test_basic_request_orient_list(self, client):
        """Test basic request with orient=list (default)."""
        # Query a range that overlaps with XAMS trading session
        # XAMS timezone is Europe/Amsterdam, session is 09:00-17:30 local time
        # 2021-01-04 was a Monday, business day
        start = "2021-01-04T08:00:00+00:00"  # 09:00 in Amsterdam (UTC+1 in winter)
        end = "2021-01-04T10:00:00+00:00"  # 10:00 UTC

        params = [
            ("mics", "XAMS"),
            ("start", start),
            ("end", end),
        ]
        response = client.get("/v1/instants", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert isinstance(result, list)
        # Should have at least one entry for XAMS
        assert len(result) > 0
        # Check structure of first entry
        entry = result[0]
        assert "mic" in entry
        assert "day_interval" in entry
        assert "start" in entry["day_interval"]
        assert "end" in entry["day_interval"]
        assert "business_day" in entry
        assert "tags" in entry

    def test_basic_request_orient_exchange(self, client):
        """Test request with orient=exchange."""
        start = "2021-01-04T08:00:00+00:00"
        end = "2021-01-04T10:00:00+00:00"

        params = [
            ("mics", "XAMS"),
            ("mics", "XLON"),
            ("start", start),
            ("end", end),
            ("orient", "exchange"),
        ]
        response = client.get("/v1/instants", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert isinstance(result, dict)
        # Should have both MICs as keys
        assert "XAMS" in result
        assert "XLON" in result
        # Values should be lists
        assert isinstance(result["XAMS"], list)
        assert isinstance(result["XLON"], list)

    def test_timezone_iana(self, client):
        """Test timezone parameter with IANA timezone name."""
        start = "2021-01-04T08:00:00+00:00"
        end = "2021-01-04T10:00:00+00:00"

        params = [
            ("mics", "XAMS"),
            ("start", start),
            ("end", end),
            ("tz", "America/New_York"),
        ]
        response = client.get("/v1/instants", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert len(result) > 0
        # Times should be in America/New_York timezone
        # Check that timezone is in the response (ISO format with offset)
        entry = result[0]
        assert "Z" not in entry["day_interval"]["start"]  # Not UTC

    def test_timezone_utc_offset(self, client):
        """Test timezone parameter with UTC offset."""
        start = "2021-01-04T08:00:00+00:00"
        end = "2021-01-04T10:00:00+00:00"

        params = [
            ("mics", "XAMS"),
            ("start", start),
            ("end", end),
            ("tz", "+05:30"),
        ]
        response = client.get("/v1/instants", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert len(result) > 0

    def test_timezone_fallback_from_query(self, client):
        """Test timezone fallback when both start and end have same tz."""
        start = "2021-01-04T08:00:00+01:00"
        end = "2021-01-04T10:00:00+01:00"

        params = [
            ("mics", "XAMS"),
            ("start", start),
            ("end", end),
        ]
        response = client.get("/v1/instants", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert len(result) > 0

    def test_timezone_error_mismatched(self, client):
        """Test error when timezone omitted and start/end have different timezones."""
        start = "2021-01-04T08:00:00+00:00"
        end = "2021-01-04T10:00:00+01:00"

        params = [
            ("mics", "XAMS"),
            ("start", start),
            ("end", end),
        ]
        response = client.get("/v1/instants", params=params)

        # Should return an error
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_business_day_filter_true(self, client):
        """Test filtering for business days only."""
        # Range covering a weekend (Saturday)
        start = "2021-01-02T00:00:00+00:00"
        end = "2021-01-05T00:00:00+00:00"

        params = [
            ("mics", "XAMS"),
            ("start", start),
            ("end", end),
            ("business_day", "true"),
        ]
        response = client.get("/v1/instants", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # All entries should be business days
        for entry in result:
            assert entry["business_day"] is True
            assert "session_interval" in entry

    def test_business_day_filter_false(self, client):
        """Test filtering for non-business days only."""
        # Range covering a weekend
        start = "2021-01-02T00:00:00+00:00"
        end = "2021-01-04T00:00:00+00:00"

        params = [
            ("mics", "XAMS"),
            ("start", start),
            ("end", end),
            ("business_day", "false"),
        ]
        response = client.get("/v1/instants", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # All entries should be non-business days
        for entry in result:
            assert entry["business_day"] is False
            assert "session_interval" not in entry or entry["session_interval"] is None

    def test_half_open_interval_overlap_session_ends_at_query_start(self, client):
        """Test half-open interval: session [09:00, 17:30) doesn't overlap with query [17:30, ...)."""
        # XAMS session on 2021-01-04 was 09:00-17:30 local time
        # In UTC (winter time UTC+1): 08:00-16:30
        # Query starting at 16:30 UTC should NOT include this session
        start = "2021-01-04T16:30:00+00:00"
        end = "2021-01-04T18:00:00+00:00"

        params = [
            ("mics", "XAMS"),
            ("start", start),
            ("end", end),
            ("business_day", "true"),
        ]
        response = client.get("/v1/instants", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # Should not include the business day from 2021-01-04
        for entry in result:
            # If we get any results, they should not be from 2021-01-04 session
            assert (
                entry.get("day_interval", {}).get("start", "")
                != "2021-01-04T08:00:00+00:00"
            )

    def test_half_open_interval_overlap_session_starts_at_query_end(self, client):
        """Test half-open interval: session [08:00, 16:30) doesn't overlap with query [..., 08:00)."""
        start = "2021-01-04T06:00:00+00:00"
        end = "2021-01-04T08:00:00+00:00"

        params = [
            ("mics", "XAMS"),
            ("start", start),
            ("end", end),
            ("business_day", "true"),
        ]
        response = client.get("/v1/instants", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # Should include the business day from 2021-01-04
        assert len(result) == 1

    def test_non_trading_day_has_day_interval(self, client):
        """Test that non-trading days have day_interval (midnight to midnight in local tz)."""
        # Query for a Sunday (2021-01-03 was a Sunday)
        start = "2021-01-03T00:00:00+00:00"
        end = "2021-01-04T00:00:00+00:00"

        params = [
            ("mics", "XAMS"),
            ("start", start),
            ("end", end),
            ("business_day", "false"),
        ]
        response = client.get("/v1/instants", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert len(result) > 0
        # Check that non-business day has day_interval
        entry = result[0]
        assert "day_interval" in entry
        assert "start" in entry["day_interval"]
        assert "end" in entry["day_interval"]
        # Should span the full day in local timezone
        # XAMS is Europe/Amsterdam, midnight to midnight local
        # In winter UTC+1: 2021-01-02T23:00:00Z to 2021-01-03T23:00:00Z
        day_start = entry["day_interval"]["start"]
        assert "2021-01-03" in day_start or "2021-01-02" in day_start

    def test_session_interval_only_for_business_days(self, client):
        """Test that session_interval is only present for business days."""
        start = "2021-01-02T00:00:00+00:00"  # Saturday
        end = "2021-01-05T00:00:00+00:00"  # Tuesday

        params = [
            ("mics", "XAMS"),
            ("start", start),
            ("end", end),
        ]
        response = client.get("/v1/instants", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert len(result) > 0
        for entry in result:
            if entry["business_day"]:
                assert "session_interval" in entry
                assert entry["session_interval"] is not None
            else:
                # Non-business days should not have session_interval
                assert (
                    "session_interval" not in entry
                    or entry.get("session_interval") is None
                )

    def test_include_tags(self, client):
        """Test include_tags filter."""
        start = "2021-01-01T00:00:00+00:00"
        end = "2021-02-01T00:00:00+00:00"

        params = [
            ("mics", "XAMS"),
            ("start", start),
            ("end", end),
            ("include_tags", "holiday"),
        ]
        response = client.get("/v1/instants", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # All entries should have holiday tag
        for entry in result:
            assert "holiday" in entry["tags"]

    def test_exclude_tags(self, client):
        """Test exclude_tags filter."""
        start = "2021-01-01T00:00:00+00:00"
        end = "2021-01-10T00:00:00+00:00"

        params = [
            ("mics", "XAMS"),
            ("start", start),
            ("end", end),
            ("exclude_tags", "weekend"),
        ]
        response = client.get("/v1/instants", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        # No entries should have weekend tag
        for entry in result:
            assert "weekend" not in entry["tags"]

    def test_multiple_mics(self, client):
        """Test with multiple MICs."""
        start = "2021-01-04T08:00:00+00:00"
        end = "2021-01-04T10:00:00+00:00"

        params = [
            ("mics", "XAMS"),
            ("mics", "XLON"),
            ("mics", "XSWX"),
            ("start", start),
            ("end", end),
        ]
        response = client.get("/v1/instants", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert len(result) > 0
        # Should have entries for all requested MICs
        mics_in_result = {entry["mic"] for entry in result}
        assert "XAMS" in mics_in_result
        assert "XLON" in mics_in_result
        assert "XSWX" in mics_in_result

    def test_orient_exchange_includes_empty_lists(self, client):
        """Test that orient=exchange includes MICs with no overlapping days as empty lists."""
        # Query a range in the distant past where there's no data
        start = "1990-01-01T00:00:00+00:00"
        end = "1990-01-02T00:00:00+00:00"

        params = [
            ("mics", "XAMS"),
            ("mics", "XLON"),
            ("start", start),
            ("end", end),
            ("orient", "exchange"),
        ]
        response = client.get("/v1/instants", params=params)

        assert response.status_code == HTTPStatus.OK
        result = response.json()
        assert isinstance(result, dict)
        # Should have both MICs as keys
        assert "XAMS" in result
        assert "XLON" in result
        # Values should be lists (possibly empty)
        assert isinstance(result["XAMS"], list)
        assert isinstance(result["XLON"], list)
