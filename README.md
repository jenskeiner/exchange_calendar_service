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

### Container image

For easy deployment, the service is available as a ready-to-use container image
on [GitHub Container Registry](https://github.com/jenskeiner/exchange_calendar_service/pkgs/container/exchange_calendar_service).

```bash
docker run -it --rm -p 8080:8080 ghcr.io/jenskeiner/exchange_calendar_service:latest
```

## Examples

Assuming the service is running on http://localhost:8080, here are some examples using [curl](https://curl.se). Note
that you can also conveniently use the auto-generated API docs at http://localhost:8080/docs to try out the endpoints.

### Supported exchanges

```bash
curl "http://localhost:8080/v1/exchanges"
```

returns a list of supported exchange MIC codes.

```json
[
  "XAMS",
  "XBRU",
  "XBUD",
  "XCSE",
  "XDUB",
  "XETR",
  "XHEL",
  "XIST",
  "XLIS",
  "XLON",
  "XMAD",
  "XOSL",
  "XPAR"
]
```

### Information about a specific exchange

```bash
curl "http://localhost:8080/v1/exchanges/XLON"
```

returns Information about the London Stock Exchange.

```json
{
  "mic": "XLON",
  "tz": "Europe/London"
}
```

### Describe a day on an exchange

```bash
curl "http://localhost:8080/v1/exchanges/XLON/days/2024-03-12"
```

Result (business day):

```json
{
  "date": "2024-03-12",
  "name": null,
  "tags": [
    "regular"
  ],
  "business_day": true,
  "session": {
    "open": "08:00:00",
    "close": "16:30:00"
  }
}
```

```bash
curl "http://localhost:8080/v1/exchanges/XLON/days/2024-12-15"
```

Result (non-business day):

```json
{
  "date": "2024-12-15",
  "name": null,
  "tags": [
    "weekend"
  ],
  "business_day": false
}
```

### Query days in a date range:

```bash
curl "http://localhost:8080/v1/exchanges/XLON/days?start=2024-12-23&end=2024-12-27"
```

Returns a list of descriptions of the days in range.

```json
[
  {
    "date": "2024-12-23",
    "name": null,
    "tags": [
      "regular"
    ],
    "business_day": true,
    "session": {
      "open": "08:00:00",
      "close": "16:30:00"
    }
  },
  {
    "date": "2024-12-24",
    "name": "Christmas Eve",
    "tags": [
      "special close"
    ],
    "business_day": true,
    "session": {
      "open": "08:00:00",
      "close": "12:30:00"
    }
  },
  {
    "date": "2024-12-25",
    "name": "Christmas",
    "tags": [
      "holiday"
    ],
    "business_day": false
  },
  {
    "date": "2024-12-26",
    "name": "Boxing Day",
    "tags": [
      "holiday"
    ],
    "business_day": false
  },
  {
    "date": "2024-12-27",
    "name": null,
    "tags": [
      "regular"
    ],
    "business_day": true,
    "session": {
      "open": "08:00:00",
      "close": "16:30:00"
    }
  }
]
```

## Configuration

The service can be configured via an `.env` file and/or environment variables. Environment variables must use the
prefix `EXCHANGE_CALENDAR_SERVICE__` to map to the correct setting.

Here's an example `.env` file:

```env
exchanges='["XLON", "XNYS"]'  # Limit to these exchanges.
init=customize:init  # Set to a callable to customize calendars on startup. Format: `module:callable`.
```

Environment variables to the same effect:

```bash
export EXCHANGE_CALENDAR_SERVICE_EXCHANGES='["XLON", "XNYS"]'
export EXCHANGE_CALENDAR_SERVICE_INIT="customize:init"
```

### Limiting the supported exchanges

By default, the service will support all available exchanges. In some situations, it may be convenient to limit the
supported exchanges to a subset of the available exchanges. Particularly, limiting the number of exchanges improves the
startup time of the service. This is because [exchange_calendars](https://github.com/gerrymanoim/exchange_calendars)
initializes session data on creation of each exchange calendar. This data is not exposed via this service, but
instantiating a lot of calendars can take a noticeable amount of time.

### Customization hook

Programmatic customizations can be done by pointing to a suitable callable via `<module_name>:<callable_name>`; see the
example in the [customize](./customize) directory pointed to by `customize:init`. On startup, the service will import
the callable and invoke it with the settings object as the single argument.

This can be used to apply any customizations to the calendars, e.g. adding new calendars, removing existing calendars,
registering calendar aliases, et cetera. See the [example](./customize/__init__.py).

## API Reference

### Response Model

The response JSON Schema for a single day on a single exchange looks like this:

```json
{
  "$defs": {
    "BusinessDay": {
      "properties": {
        "date": {
          "format": "date",
          "title": "Date",
          "type": "string"
        },
        "name": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Name"
        },
        "tags": {
          "items": {
            "$ref": "#/$defs/Tags"
          },
          "title": "Tags",
          "type": "array",
          "uniqueItems": true
        },
        "business_day": {
          "const": true,
          "default": true,
          "title": "Is Business Day",
          "type": "boolean"
        },
        "session": {
          "$ref": "#/$defs/Session"
        }
      },
      "required": [
        "date",
        "tags",
        "session"
      ],
      "title": "BusinessDay",
      "type": "object"
    },
    "NonBusinessDay": {
      "properties": {
        "date": {
          "format": "date",
          "title": "Date",
          "type": "string"
        },
        "name": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Name"
        },
        "tags": {
          "items": {
            "$ref": "#/$defs/Tags"
          },
          "title": "Tags",
          "type": "array",
          "uniqueItems": true
        },
        "business_day": {
          "const": false,
          "default": false,
          "title": "Is Business Day",
          "type": "boolean"
        }
      },
      "required": [
        "date",
        "tags"
      ],
      "title": "NonBusinessDay",
      "type": "object"
    },
    "Session": {
      "properties": {
        "open": {
          "format": "time",
          "title": "Open",
          "type": "string"
        },
        "close": {
          "format": "time",
          "title": "Close",
          "type": "string"
        }
      },
      "required": [
        "open",
        "close"
      ],
      "title": "Session",
      "type": "object"
    },
    "Tags": {
      "enum": [
        "special open",
        "special close",
        "quarterly expiry",
        "monthly expiry",
        "month end",
        "holiday",
        "weekend",
        "regular"
      ],
      "title": "Tags",
      "type": "string"
    }
  },
  "discriminator": {
    "mapping": {
      "False": "#/$defs/NonBusinessDay",
      "True": "#/$defs/BusinessDay"
    },
    "propertyName": "business_day"
  },
  "oneOf": [
    {
      "$ref": "#/$defs/BusinessDay"
    },
    {
      "$ref": "#/$defs/NonBusinessDay"
    }
  ]
}
```

The fields `date`, `business_day` and `tags` are always present:

- `date`: The date in ISO format.
- `business_day`: A boolean indicating whether the day is a trading day or not.
- `tags`: A list of tags associated with the day.

The response may optionally provide a `name` field, e.g. for holidays or special days.

If the day is a business day, the response contains the `session` field which provides the start and end time of the
trading session.

### Tags

While the `business_day` field indicates whether a day is a business days or not, tags allow to attach more
fine-grained information. Each day can carry multiple tags, e.g. "holiday" and "weekend". The meaning of the tags is as
follows:

- `special open`: The trading session starts at a non-standard time, typically later than usual.
- `special close`: The trading session ends at a non-standard time, typically earlier than usual.
- `quarterly expiry`: Indicates quarterly expiry days, typically the third Thursday in March, June, September and
  December.
- `monthly expiry`: Indicates monthly expiry days, typically the third Thursday in the other months.
- `month end`: The last trading day in the respective month.
- `holiday`: A holiday on which the exchange is closed.
- `weekend`: A weekend day on which the exchange is regularly closed.
- `regular`: The day has regular trading session times.

All endpoints are under `/v1/`.

### Reference Endpoints

#### GET /exchanges

Get list of supported exchange MIC codes.

**Example: **

```bash
curl http: //localhost:8080/v1/exchanges
```

Response:

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

Response:

```json
{
  "mic": "XLON",
  "tz": "Europe/London"
}
```

### Single Exchange Endpoints

These endpoints return information about one or more days for a single exchange.

#### GET /exchanges/{mic}/days/{day}

Describe a single day for an exchange.

**Path Parameters:**

- `mic` - MIC code of the exchange
- `day` - Date in ISO format (e.g., `2024-12-25`)

**Response:** A `Day` object with either `business_day: true` (business day) or `business_day: false` (
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
  "business_day": false
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
  "business_day": true,
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
    "business_day": false
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
    "business_day": false
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
