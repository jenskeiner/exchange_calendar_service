# Exchange Calendar Service

[![PyPI](https://img.shields.io/pypi/v/exchange-calendar-service)](https://pypi.org/project/exchange-calendar-service/)
[![Python Support](https://img.shields.io/pypi/pyversions/exchange_calendar_service)](https://pypi.org/project/exchange-calendar-service/)
[![PyPI Downloads](https://img.shields.io/pypi/dd/exchange-calendar-service)](https://pypi.org/project/exchange-calendar-service/)

An simple HTTP service for querying exchange calendars for stock exchanges. Built on top
of [exchange_calendars](https://github.com/gerrymanoim/exchange_calendars)
and [exchange_calendars_extensions](https://github.com/jenskeiner/exchange_calendars_extensions).

## Features

- RESTful API for exchange calendar queries.
- Support for 60+ global exchanges.
- Query holidays, special open/close days, monthly and quarterly expiry days, and more.
- Support for customization hooks.
- Docker image available for easy deployment.

## Installation

The package requires Python 3.11 or later.

### As a tool

If you are primarily interested in running the service as a tool and without any customizations, you can use
[uv](https://github.com/astral-sh/uv)'s tool support:

```bash
uvx exchange-calendar-service
```

This will start the service via [Uvicorn](https://uvicorn.dev) on http://localhost:8080 by default. See
http://localhost:8080/docs for auto-generated API docs.

Alternatively, install and run via [pipx](https://github.com/pypa/pipx):

```bash
pipx install exchange-calendar-service
exchange-calendar-service
```

### As a dependency

Add the [PyPI package](https://pypi.org/project/exchange-calendar-service/) as a dependency to your Python project via
[uv](https://github.com/astral-sh/uv):

```bash
uv add exchange-calendar-service
```

Or edit `pyproject.toml` directly:

```toml
[project]
dependencies = [
    "exchange-calendar-service=^0.1.0",
]
```

In a Python virtual environment, you can start the service via a script:

```bash
exchange-calendar-service
```

or by running the Python module directly:

```bash
python -m exchange_calendar_service
```

### Container Image

For easy deployment, the service is available as a ready-to-use container image
on [GitHub Container Registry](https://github.com/jenskeiner/exchange_calendar_service/pkgs/container/exchange_calendar_service).

```bash
docker run -it --rm -p 8080:8080 ghcr.io/jenskeiner/exchange_calendar_service:latest
```

## Examples

Assuming the service is running on http://localhost:8080, here are some examples using [curl](https://curl.se). Note
that you can also conveniently use the auto-generated API docs at http://localhost:8080/docs to try out the endpoints.

### List supported exchanges:

```bash
curl "http://localhost:8080/v1/exchanges"
```

### Get information about a specific exchange:

```bash
curl "http://localhost:8080/v1/exchanges/XLON"
```

### Describe a specific day:

```bash
curl "http://localhost:8080/v1/exchanges/XLON/days/2024-12-25"
```

Result (non-business day):

```json
{
  "date": "2024-12-25",
  "name": "Christmas Day",
  "tags": [
    "holiday"
  ],
  "is_business_day": false
}
```

Result (business day):

```json
{
  "date": "2024-12-24",
  "name": null,
  "tags": [
    "regular"
  ],
  "is_business_day": true,
  "session": {
    "open": "08:00:00",
    "close": "16:30:00"
  }
}
```

### Query days in a date range:

```bash
curl "http://localhost:8080/v1/exchanges/XLON/days?start=2024-12-24&end=2024-12-27"
```

## Configuration

Configuration can be done via an `.env` file and/or via environment variables, with the environment variables taking
precedence. Environment variables must use the prefix `EXCHANGE_CALENDAR_SERVICE__` to map to the correct setting.

Here's an example `.env` file:

```env
exchanges='["XLON", "XNYS"]'  # Limit the service to these calendars, identified by their MIC codes.
init=customize:init  # Set to a callable to customize calendars on startup. Format: `module:callable`.
```

And here's the corresponding environment variables to the same effect:

```bash
export EXCHANGE_CALENDAR_SERVICE_EXCHANGES='["XLON", "XNYS"]'
export EXCHANGE_CALENDAR_SERVICE_INIT="customize:init"
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

## API Reference

All endpoints are under `/v1/`.

### Reference Endpoints

#### GET /exchanges

Get list of supported exchange MIC codes.

**Query Parameters:** None

**Example:**

```bash
curl http://localhost:8080/v1/exchanges
```

```json
[
  "XAMS",
  "XLON",
  "XNYS",
  "XSWX"
]
```

#### GET /exchanges/{mic}

Get information about a specific exchange.

**Path Parameters:**

- `mic` - MIC code of the exchange

**Example:**

```bash
curl http://localhost:8080/v1/exchanges/XLON
```

```json
{
  "mic": "XLON",
  "tz": "Europe/London"
}
```

### Day Endpoints

#### GET /exchanges/{mic}/days/{day}

Describe a specific day for an exchange.

**Path Parameters:**

- `mic` - MIC code of the exchange
- `day` - Date in ISO format (e.g., `2024-12-25`)

**Response:** A `Day` object with either `is_business_day: true` (business day) or `is_business_day: false` (
non-business day).

**Example:**

```bash
curl "http://localhost:8080/v1/exchanges/XLON/days/2024-12-25"
```

```json
{
  "date": "2024-12-25",
  "name": "Christmas Day",
  "tags": [
    "holiday"
  ],
  "is_business_day": false
}
```

**Business day response:**

```json
{
  "date": "2024-12-24",
  "name": null,
  "tags": [
    "regular"
  ],
  "is_business_day": true,
  "session": {
    "open": "08:00:00",
    "close": "16:30:00"
  }
}
```

#### GET /exchanges/{mic}/days

Get days in a date range that match criteria.

**Path Parameters:**

- `mic` - MIC code of the exchange

**Query Parameters:**

- `start` (required) - Start date in ISO format (inclusive)
- `end` (required) - End date in ISO format (inclusive)
- `business_day` (optional) - Filter to only business days (`true`) or non-business days (`false`)
- `include_tags` (optional, repeatable) - Only include days with all of the given tags
- `exclude_tags` (optional, repeatable) - Exclude days with any of the given tags
- `order` (optional, default: `asc`) - Sort order: `asc` or `desc`
- `limit` (optional) - Maximum number of days to return

**Available tags:** `special open`, `special close`, `quarterly expiry`, `monthly expiry`, `month end`, `holiday`,
`weekend`, `regular`

**Example:**

```bash
curl "http://localhost:8080/v1/exchanges/XLON/days?start=2024-12-24&end=2024-12-27&business_day=false"
```

```json
[
  {
    "date": "2024-12-25",
    "name": "Christmas Day",
    "tags": [
      "holiday"
    ],
    "is_business_day": false
  }
]
```

#### GET /exchanges/{mic}/days/{day}/next

Get the next (or previous) days matching criteria relative to a reference day.

**Path Parameters:**

- `mic` - MIC code of the exchange
- `day` - Reference date in ISO format

**Query Parameters:**

- `direction` (optional, default: `forward`) - Search direction: `forward` or `backward`
- `inclusive` (optional, default: `true`) - Include the reference day if it matches
- `end` (optional) - End date to bound the search (inclusive)
- `business_day` (optional) - Filter to only business days or non-business days
- `include_tags` (optional, repeatable) - Only include days with all of the given tags
- `exclude_tags` (optional, repeatable) - Exclude days with any of the given tags
- `limit` (optional) - Maximum number of days to return
- `order` (optional, default: `asc`) - Sort order of results: `asc` or `desc`

**Example:**

```bash
curl "http://localhost:8080/v1/exchanges/XLON/days/2024-12-20/next?direction=forward&limit=3&business_day=false"
```

```json
[
  {
    "date": "2024-12-25",
    "name": "Christmas Day",
    "tags": [
      "holiday"
    ],
    "is_business_day": false
  }
]
```

## Customization

The service can be customized at startup by providing init functions. These functions receive the `Settings` instance
and
can modify calendars, register aliases, or add new ones.

### Init via Environment Variable

Set `EXCHANGE_CALENDAR_SERVICE_INIT` to a module path pointing to a callable, in the format `module:callable`. The
callable must accept one argument (`Settings`).

```bash
export EXCHANGE_CALENDAR_SERVICE_INIT="customize:init"
uv run python -m exchange_calendar_service.app
```

### Init via Entrypoints

Init functions can also be automatically discovered
via [entry points](https://packaging.python.org/en/latest/specifications/entry-points/)
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
    ec.register_calendar_alias("XNAS", "XNYS")

    # Replace a calendar with a custom version (force=True)
    # ec.register_calendar_type("XTAE", CustomCalendar, force=True)
```

The init function can:

- **Replace calendars** - Use `ec.register_calendar_type(name, calendar_class, force=True)`
- **Register aliases** - Use `ec.register_calendar_alias(alias, target_calendar)`
- **Add new calendars** - Use `ec.register_calendar_type(name, calendar_class)`

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

The configured hooks run `pyupgrade` (targeting Python 3.12+), `ruff` (linter), and `ruff-format` (formatter).

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
  -e EXCHANGE_CALENDAR_SERVICE_EXCHANGES='["XLON"]' \
  ghcr.io/jenskeiner/exchange_calendar_service
```

The service listens on port 8080.

## License

Apache-2.0
