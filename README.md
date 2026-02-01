# Exchange Calendar Service

An HTTP service for querying trading and holiday calendars for global stock exchanges. Built on [exchange_calendars_extensions](https://github.com/jenskeiner/exchange_calendars_extensions), it covers 100+ exchanges worldwide.

## Features

- RESTful API for exchange calendar queries
- Support for 100+ global exchanges via MIC codes
- Holiday and special trading day queries
- Business day classification and date arithmetic
- Timezone-aware operations
- Custom calendar support via init hooks
- Efficient caching with configurable TTL
- Docker containerization support

## Installation

```bash
pip install exchange-calendar-service
```

```bash
uv pip install exchange-calendar-service
```

Requires Python 3.11 or later.

## Quick Start

Start the service:

```bash
uv run exchange_calendar-service
# or
uv run python -m exchange_calendar_service.app
```

The service runs on http://localhost:8080 by default. Auto-generated API docs are available at `/docs`.

Example: Check if a date is a trading day:

```bash
curl "http://localhost:8080/v1/classify_day?day=2024-12-25&mic=XLON"
```

```json
{
  "date": "2024-12-25",
  "type": "holiday",
  "is_business_day": false,
  "name": "Christmas Day"
}
```

## Configuration

Configuration via environment variables:

| Variable | Description |
|----------|-------------|
| `EXCHANGE_CALENDAR_SERVICE_CHANGES_API_KEY` | Optional API key. Enables the `/update` endpoint for injecting calendar changes. |
| `EXCHANGE_CALENDAR_SERVICE_INIT` | Optional init function to customize calendars. Format: `module:callable`. Invoked on startup. |
| `EXCHANGE_CALENDAR_SERVICE_EXCHANGES` | Optional dict of supported exchanges. Format: `{"XLON": "XLON", "XNYS": "XNYS"}`. Default: all exchanges. |

Examples:

```bash
export EXCHANGE_CALENDAR_SERVICE_CHANGES_API_KEY="secret-key"
export EXCHANGE_CALENDAR_SERVICE_INIT="myapp:customize_calendars"
export EXCHANGE_CALENDAR_SERVICE_EXCHANGES='{"XLON": "XLON", "XNYS": "XNYS"}'
```

## API Reference

All endpoints are under `/v1/`.

### GET /mics

Get list of valid MIC codes for querying exchanges.

**Query Parameters:** None

**Example:**
```bash
curl http://localhost:8080/v1/mics
```

```json
["XAMS", "XLON", "XSWX"]
```

### GET /mic2name

Get mapping of MIC codes to exchange names.

**Query Parameters:** None

**Example:**
```bash
curl http://localhost:8080/v1/mic2name
```

```json
{"XAMS": "XAMS", "XLON": "XLON", "XSWX": "XSWX"}
```

### GET /timezone

Get timezone for exchanges.

**Query Parameters:**
- `mic` (optional) - Single MIC to query. If omitted, returns all exchanges.
- `standardise` (optional, default: `true`) - Return short timezone name (e.g., `CET`) or full IANA name (e.g., `Europe/Berlin`)

**Example:**
```bash
curl "http://localhost:8080/v1/timezone?mic=XLON&standardise=true"
```

```json
[{"mic": "XLON", "tz": "WET"}]
```

### GET /special_days

Get holidays, special opens/closes, and expiry dates for an exchange.

**Query Parameters:**
- `mic` (required) - MIC code
- `year` (optional) - Year to query. Defaults to current year.
- `tz` (optional) - Timezone for special open/close times (e.g., `CET`, `Europe/London`)

**Example:**
```bash
curl "http://localhost:8080/v1/special_days?mic=XLON&year=2024"
```

```json
[
  {
    "date": "2024-01-01",
    "type": "holiday",
    "is_business_day": false,
    "name": "New Year's Day"
  },
  {
    "date": "2024-03-28",
    "type": "holiday",
    "is_business_day": false,
    "name": "Maundy Thursday"
  },
  {
    "date": "2024-03-28",
    "type": "special close",
    "is_business_day": true,
    "time": "12:30:00",
    "tz": "Europe/London",
    "name": "ad-hoc special close"
  },
  {
    "date": "2024-03-15",
    "type": "monthly expiry",
    "is_business_day": true,
    "name": "monthly expiry"
  }
]
```

### GET /classify_day

Classify a specific day type for one or all exchanges.

**Query Parameters:**
- `day` (required) - Date in ISO format (e.g., `2024-12-25`)
- `mic` (optional) - Single MIC to query. If omitted, returns all exchanges grouped by classification.
- `tz` (optional) - Timezone for special open/close times

**Example (single MIC):**
```bash
curl "http://localhost:8080/v1/classify_day?day=2024-12-25&mic=XLON"
```

```json
{
  "date": "2024-12-25",
  "type": "holiday",
  "is_business_day": false,
  "name": "Christmas Day"
}
```

**Example (all exchanges):**
```bash
curl "http://localhost:8080/v1/classify_day?day=2024-12-25"
```

```json
[
  {
    "date": "2024-12-25",
    "type": "holiday",
    "is_business_day": false,
    "name": "Christmas Day",
    "mics": ["XLON"]
  },
  {
    "date": "2024-12-25",
    "type": "regular",
    "is_business_day": true,
    "mics": ["XAMS"]
  }
]
```

### GET /next_special_days

Get next or previous special days relative to a reference date.

**Query Parameters:**
- `day` (optional, default: today) - Reference date in ISO format
- `forward` (optional, default: `true`) - Search direction (`true` for forward, `false` for backward)
- `n` (optional, default: `1`) - Number of days to return
- `inclusive` (optional, default: `true`) - Include the reference day if it matches
- `mic` (optional) - Comma-separated list of MICs to filter. If omitted, searches all exchanges.
- `range` (optional) - Maximum search window in days
- `tz` (optional) - Timezone for special open/close times
- `exclude_tags` (optional, repeatable) - Exclude dates with specified tags

**Example:**
```bash
curl "http://localhost:8080/v1/next_special_days?day=2024-12-20&forward=true&n=3&mic=XLON"
```

```json
[
  [
    {
      "date": "2024-12-25",
      "classifications": [
        {
          "date": "2024-12-25",
          "type": "holiday",
          "is_business_day": false,
          "name": "Christmas Day",
          "mics": ["XLON"]
        }
      ]
    }
  ],
  200
]
```

Returns a tuple of `[results, status]` where status is `200` on success or `416` if range exceeded.

### GET /next_business_days

Get next or previous business days relative to a reference date.

**Query Parameters:**
- `day` (optional, default: today) - Reference date in ISO format
- `forward` (optional, default: `true`) - Search direction
- `n` (optional, default: `1`) - Number of days to return
- `inclusive` (optional, default: `true`) - Include the reference day if it's a business day
- `mic` (optional) - Comma-separated list of MICs to filter
- `range` (optional) - Maximum search window in days
- `tz` (optional) - Timezone for special open/close times
- `exclude_tags` (optional, repeatable) - Exclude dates with specified tags

**Example:**
```bash
curl "http://localhost:8080/v1/next_business_days?day=2024-12-20&forward=true&n=5"
```

```json
[
  [
    {
      "date": "2024-12-20",
      "classifications": [
        {
          "date": "2024-12-20",
          "type": "regular",
          "is_business_day": true,
          "mics": ["XAMS", "XLON"]
        }
      ]
    }
  ],
  200
]
```

Business days include regular trading days and special open/close days. Returns `[results, status]` format.

## Customization

The service can be customized at startup by providing an init function via the `EXCHANGE_CALENDAR_SERVICE_INIT` environment variable. This function receives the `Settings` instance and can modify calendars, register aliases, or add new ones.

### Setting the Init Function

Set `EXCHANGE_CALENDAR_SERVICE_INIT` to a module path pointing to a callable, in the format `module:callable`. The callable must accept one argument (`Settings`).

```bash
export EXCHANGE_CALENDAR_SERVICE_INIT="customize:init"
uv run python -m exchange_calendar_service.app
```

### Example: customize/__init__.py

```python
import logging

import exchange_calendars as ec

from exchange_calendar_service.app.settings import Settings

log = logging.getLogger(__name__)


def init(settings: Settings) -> None:
    """Customize exchange calendars at startup."""
    log.info("Customizing exchange calendars...")

    # Register an alias for an existing calendar
    ec.calendar_utils.register_calendar_alias("XNAS", "XNYS")

    # Replace a calendar with a custom version (force=True)
    # ec.calendar_utils.register_calendar_type("XTAE", CustomCalendar, force=True)
```

The init function can:
- **Replace calendars** - Use `register_calendar_type(name, calendar_class, force=True)`
- **Register aliases** - Use `register_calendar_alias(alias, target_calendar)`
- **Add new calendars** - Use `register_calendar_type(name, calendar_class)`

### Extended Example

See `customize/xtae.py` for a complete example that extends the Tel Aviv Stock Exchange (`XTAE`) calendar with custom holiday handling logic.

## Development

The project requires Python 3.11 or later.

### Testing

Run the full test suite with coverage:

```bash
uv run pytest -v tests/ --cov=exchange_calendar_service --cov-fail-under=80
```

Coverage gate: 80% minimum.

### Pre-commit Hooks

Install and enable pre-commit hooks:

```bash
pre-commit install
```

The configured hooks run `pyupgrade` (targeting Python 3.11+), `ruff` (linter), and `ruff-format` (formatter).

## Deployment

The service uses uvicorn. A Dockerfile is provided.

### Building the Docker Image

From the project root:

```bash
docker build -f docker/Dockerfile -t exchange-calendar-service .
```

### Running the Container

```bash
docker run -p 8080:8080 exchange-calendar-service
```

### Environment Variables

Pass configuration via `-e` flags:

```bash
docker run -p 8080:8080 \
  -e EXCHANGE_CALENDAR_SERVICE_CHANGES_API_KEY=your-key \
  -e EXCHANGE_CALENDAR_SERVICE_EXCHANGES='{"XLON": "XLON"}' \
  exchange-calendar-service
```

The service listens on port 8080.

## License

Apache-2.0
