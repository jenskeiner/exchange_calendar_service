# Exchange Calendar Service

[![PyPI](https://img.shields.io/pypi/v/exchange-calendar-service)](https://pypi.org/project/exchange-calendar-service/)
[![Python Support](https://img.shields.io/pypi/pyversions/exchange_calendar_service)](https://pypi.org/project/exchange-calendar-service/)
[![PyPI Downloads](https://img.shields.io/pypi/dd/exchange-calendar-service)](https://pypi.org/project/exchange-calendar-service/)

An HTTP service for querying trading calendars for stock exchanges. Built
on [exchange_calendars](https://github.com/gerrymanoim/exchange_calendars) and
[exchange_calendars_extensions](https://github.com/jenskeiner/exchange_calendars_extensions), it covers 60+ exchanges
worldwide.

Requires Python 3.11 or later.

## Features

- RESTful API for exchange calendar queries
- Support for 60+ global exchanges
- Query holidays, special open/close trading days, witching days and more
- Timezone-aware operations
- Support for custom calendars and calendar modifications via init hooks
- Efficient caching with configurable TTL
- Docker image available for easy deployment

## Installation

### As a dependency

The package is available on [PyPI](https://pypi.org/project/exchange-calendar-service/) and can be added as a dependency
to your project via [uv](https://github.com/astral-sh/uv) or any other suitable package/dependency management tool.

```bash
uv add exchange-calendar-service
```

### As a tool

If you are primarily interested in running the service as a tool and without any customization, you can use
[uv](https://github.com/astral-sh/uv)'s tool support

```bash
uvx exchange-calendar-service
```

or install via [pipx](https://github.com/pypa/pipx)

```bash
pipx install exchange-calendar-service
```

## Quick Start

With the package installed in a virtual environment (and with that environment activated), you can start the service
as a script

```bash
exchange_calendar-service
```

Alternatively, you invoke the Python module directly:

```bash
python -m exchange_calendar_service
```

or

```bash
uv run exchange_calendar-service
```

This will start the service via [Uvicorn](https://uvicorn.dev) on http://localhost:8080 by default. See
http://localhost:8080/docs for auto-generated API docs.

If you're using a different [ASGI](https://asgi.readthedocs.io/en/latest/) web server, point it to the module
`exchange_calendar_service:app` which is a function that returns an ASGI application.

## Examples

Assuming the service is running on http://localhost:8080, here are some examples using [curl](https://curl.se). Note
that you can also conveniently use the auto-generated API docs at http://localhost:8080/docs to try out the endpoints.

### Check if a date is a trading day:

Request:

```bash
curl "http://localhost:8080/v1/classify_day?day=2024-12-25&mic=XLON"
```

Result:

```json
{
  "date": "2024-12-25",
  "type": "holiday",
  "is_business_day": false,
  "name": "Christmas Day"
}
```

## Configuration

Configuration can be done via an `.env` file and/or via environment variables, with the environment variables taking
precedence. Environment variables must use the prefix `EXCHANGE_CALENDAR_SERVICE__` to map to the correct setting.

Here's an example `.env` file:

```env
exchanges='["XLON", "XNYS"]'  # Limit the service to these calendars, identified by their MIC codes.
init=myapp:customize_calendars  # Set to a callable to customize calendars on startup. Format: `module:callable`.
changes_api_key=secret-key  # Set to enable the `/update` endpoint for injecting calendar changes.
```

And here's the corresponding environment variables to the same effect:

```bash
EXCHANGE_CALENDAR_SERVICE_EXCHANGES='["XLON", "XNYS"]'
EXCHANGE_CALENDAR_SERVICE_INIT=customize:init
EXCHANGE_CALENDAR_SERVICE_CHANGES_API_KEY=secret-key
```

### Limiting the supported exchanges

By default, the service will support all available exchanges. In some situations, it may be convenient to limit the
supported exchanges to a subset of the available exchanges. This can be done via the `exchanges` setting, which is a
JSON array of MIC codes.

### Customizations

Customizations can be done via the `init` setting, which is a string pointing to a callable, e.g. `customize:init`. On
startup, the service will import the callable and invoke it with the settings object as an argument.

This can be used to apply any customizations to the calendars, e.g. adding new calendars, removing existing calendars,
registering calendar aliases, et cetera. See the [customization example](#customization-example).

### Changes API

When enabled, the service will expose an `/update` endpoint that allows clients to inject calendar changes. The
endpoint is protected by an API key, which must be provided via the `changes_api_key` setting. Clients must provide
the API key in the `X-API-Key` request header.

The Changes API provides a way to dynamically update calendars. This can be useful if an ad-hoc change is needed since
the underlying calendar does not (yet) reflect the change.

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
[
  "XAMS",
  "XLON",
  "XSWX"
]
```

### GET /mic2name

Get mapping of MIC codes to exchange names.

**Query Parameters:** None

**Example:**

```bash
curl http://localhost:8080/v1/mic2name
```

```json
{
  "XAMS": "XAMS",
  "XLON": "XLON",
  "XSWX": "XSWX"
}
```

### GET /timezone

Get timezone for exchanges.

**Query Parameters:**

- `mic` (optional) - Single MIC to query. If omitted, returns all exchanges.
- `standardise` (optional, default: `true`) - Return short timezone name (e.g., `CET`) or full IANA name (e.g.,
  `Europe/Berlin`)

**Example:**

```bash
curl "http://localhost:8080/v1/timezone?mic=XLON&standardise=true"
```

```json
[
  {
    "mic": "XLON",
    "tz": "WET"
  }
]
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
    "mics": [
      "XLON"
    ]
  },
  {
    "date": "2024-12-25",
    "type": "regular",
    "is_business_day": true,
    "mics": [
      "XAMS"
    ]
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
          "mics": [
            "XLON"
          ]
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
          "mics": [
            "XAMS",
            "XLON"
          ]
        }
      ]
    }
  ],
  200
]
```

Business days include regular trading days and special open/close days. Returns `[results, status]` format.

## Customization

The service can be customized at startup by providing init functions. These functions receive the `Settings` instance and
can modify calendars, register aliases, or add new ones.

### Init via Environment Variable

Set `EXCHANGE_CALENDAR_SERVICE_INIT` to a module path pointing to a callable, in the format `module:callable`. The
callable must accept one argument (`Settings`).

```bash
export EXCHANGE_CALENDAR_SERVICE_INIT="customize:init"
uv run python -m exchange_calendar_service.app
```

### Init via Entrypoints

Init functions can also be automatically discovered via [entry points](https://packaging.python.org/en/latest/specifications/entry-points/)
in the `exchange_calendar_service.init` group. All discovered entrypoints are called in the order returned by
`importlib.metadata`.

To register an entrypoint, add to your `pyproject.toml`:

```toml
[project.entry-points."exchange_calendar_service.init"]
my_customizer = "my_package:init_function"
```

Multiple packages can register entrypoints, and all will be called. This allows customization via installed dependencies
without needing to set environment variables.

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

See `customize/xtae.py` for a complete example that extends the Tel Aviv Stock Exchange (`XTAE`) calendar with custom
holiday handling logic.

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
  -e EXCHANGE_CALENDAR_SERVICE_EXCHANGES='["XLON"]' \
  exchange-calendar-service
```

The service listens on port 8080.

## License

Apache-2.0
