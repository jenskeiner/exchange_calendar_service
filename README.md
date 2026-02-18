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
  "business_day": true,
  "session": {
    "open": "08:00:00",
    "close": "16:30:00"
  },
  "tags": [
    "regular"
  ]
}
```

```bash
curl "http://localhost:8080/v1/exchanges/XLON/days/2024-12-15"
```

Result (non-business day):

```json
{
  "date": "2024-12-15",
  "business_day": false,
  "tags": [
    "weekend"
  ]
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
    "business_day": true,
    "session": {
      "open": "08:00:00",
      "close": "16:30:00"
    },
    "tags": [
      "regular"
    ]
  },
  {
    "date": "2024-12-24",
    "name": "Christmas Eve",
    "business_day": true,
    "session": {
      "open": "08:00:00",
      "close": "12:30:00"
    },
    "tags": [
      "special close"
    ]
  },
  {
    "date": "2024-12-25",
    "name": "Christmas",
    "business_day": false,
    "tags": [
      "holiday"
    ]
  },
  {
    "date": "2024-12-26",
    "name": "Boxing Day",
    "business_day": false,
    "tags": [
      "holiday"
    ]
  },
  {
    "date": "2024-12-27",
    "business_day": true,
    "session": {
      "open": "08:00:00",
      "close": "16:30:00"
    },
    "tags": [
      "regular"
    ]
  }
]
```

### Query days in a date range for multiple exchanges

```bash
curl "http://localhost:8080/v1/days?start=2024-12-23&end=2024-12-27&mics=XLON&mics=XNYS"
```

Returns a list grouped by date, where each element contains data for all requested exchanges.

```json
[
  {
    "XLON": {
      "date": "2024-12-23",
      "business_day": true,
      "session": {
        "open": "08:00:00",
        "close": "16:30:00"
      },
      "tags": [
        "regular"
      ]
    },
    "XNYS": {
      "date": "2024-12-23",
      "business_day": true,
      "session": {
        "open": "09:30:00",
        "close": "16:00:00"
      },
      "tags": [
        "regular"
      ]
    }
  },
  {
    "XLON": {
      "date": "2024-12-24",
      "name": "Christmas Eve",
      "business_day": true,
      "session": {
        "open": "08:00:00",
        "close": "12:30:00"
      },
      "tags": [
        "special close"
      ]
    },
    "XNYS": {
      "date": "2024-12-24",
      "name": "Christmas Eve",
      "business_day": true,
      "session": {
        "open": "09:30:00",
        "close": "13:00:00"
      },
      "tags": [
        "special close"
      ]
    }
  },
  {
    "XLON": {
      "date": "2024-12-25",
      "name": "Christmas",
      "business_day": false,
      "tags": [
        "holiday"
      ]
    },
    "XNYS": {
      "date": "2024-12-25",
      "name": "Christmas",
      "business_day": false,
      "tags": [
        "holiday"
      ]
    }
  },
  {
    "XLON": {
      "date": "2024-12-26",
      "name": "Boxing Day",
      "business_day": false,
      "tags": [
        "holiday"
      ]
    },
    "XNYS": {
      "date": "2024-12-26",
      "business_day": true,
      "session": {
        "open": "09:30:00",
        "close": "16:00:00"
      },
      "tags": [
        "regular"
      ]
    }
  },
  {
    "XLON": {
      "date": "2024-12-27",
      "business_day": true,
      "session": {
        "open": "08:00:00",
        "close": "16:30:00"
      },
      "tags": [
        "regular"
      ]
    },
    "XNYS": {
      "date": "2024-12-27",
      "business_day": true,
      "session": {
        "open": "09:30:00",
        "close": "16:00:00"
      },
      "tags": [
        "regular"
      ]
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

### Customization

The service support customizations by executing custom code at startup time.

### Init via Environment Variable

Set `EXCHANGE_CALENDAR_SERVICE_INIT` to a module path pointing to a callable, in the format `module:callable`. The
callable must accept one argument (`Settings`). On startup, the service will import the callable and invoke it with the
settings object as the single argument. This can be used to apply any customizations to the calendars, e.g. adding new
calendars, removing existing calendars,
registering calendar aliases, et cetera.

For example, setting `EXCHANGE_CALENDAR_SERVICE_INIT="customize:init"` will execute the `init` function from the
[customize](./customize) module. See the example for details on how calendars can be customized.

```bash
export EXCHANGE_CALENDAR_SERVICE_INIT="customize:init"
uv run python -m exchange_calendar_service.app
```

#### Via Entrypoints

Custom code can also be discovered automatically
via [entry points](https://packaging.python.org/en/latest/specifications/entry-points/)
in the `exchange_calendar_service.init` group. All discovered entrypoints are called sequentially, but in no particular
order.

To register an entrypoint, add to your `pyproject.toml`:

```toml
[project.entry-points."exchange_calendar_service.init"]
my_customizer = "my_package:init_function"
```

Multiple packages can register entrypoints, and all will be called. This allows customization via installed dependencies
without needing to set environment variables.

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
          "title": "The date of the day in ISO format (YYYY-MM-DD).",
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
          "title": "The name of the day."
        },
        "tags": {
          "items": {
            "$ref": "#/$defs/Tags"
          },
          "title": "A set of tags associated with the day.",
          "type": "array",
          "uniqueItems": true
        },
        "business_day": {
          "const": true,
          "default": true,
          "title": "Indicates that the day is a business day.",
          "type": "boolean"
        },
        "session": {
          "$ref": "#/$defs/Session",
          "title": "The trading session."
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
          "title": "The date of the day in ISO format (YYYY-MM-DD).",
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
          "title": "The name of the day."
        },
        "tags": {
          "items": {
            "$ref": "#/$defs/Tags"
          },
          "title": "A set of tags associated with the day.",
          "type": "array",
          "uniqueItems": true
        },
        "business_day": {
          "const": false,
          "default": false,
          "title": "Indicates that the day is not a business day.",
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
          "title": "The start of the trading session (HH:MM:SS).",
          "type": "string"
        },
        "close": {
          "format": "time",
          "title": "The end of the trading session (HH:MM:SS).",
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
- `business_day`: Whether the day is a business day or not.
- `tags`: A list of tags associated with the day.

The response may optionally provide a `name` field, e.g. for holidays or special days.

If the day is a business day, the response contains the `session` field which provides the start and end time of the
trading session.

*Note: Session open and close times are always in the exchange's timezone.*

### Tags

While the `business_day` partitions the days into business and non-business days, tags allow to attach more
fine-grained information to individual days. Each day can carry multiple tags, e.g. "holiday" and "weekend". The
meaning of the tags is as follows:

- `special open`: The trading session starts at a non-standard time, typically later than usual.
- `special close`: The trading session ends at a non-standard time, typically earlier than usual.
- `quarterly expiry`: Indicates quarterly expiry days, typically the third Thursday in March, June, September and
  December.
- `monthly expiry`: Indicates monthly expiry days, typically the third Thursday in the other months.
- `month end`: The last trading day in the respective month.
- `holiday`: A holiday on which the exchange is closed.
- `weekend`: A weekend day on which the exchange is regularly closed.
- `regular`: The day has regular trading session times.

#### Examples

A regular trading day:

```json
{
  "date": "2026-01-08",
  "business_day": true,
  "session": {
    "open": "08:00:00",
    "close": "16:30:00"
  },
  "tags": [
    "regular"
  ]
}
```

A regular weekend day:

```json
{
  "date": "2026-01-10",
  "business_day": false,
  "tags": [
    "weekend"
  ]
}
```

A holiday that would otherwise be a business day:

```json
{
  "date": "2026-01-01",
  "name": "New Year's Day",
  "business_day": false,
  "tags": [
    "holiday"
  ]
}
```

A holiday that is also a wekend day:

```json
{
  "date": "2022-12-25",
  "name": "Christmas",
  "tags": [
    "weekend",
    "holiday"
  ],
  "business_day": false
}
```

A special close day that is also the last trading day of a month:

```json
{
  "date": "2022-12-30",
  "name": "New Year's Eve",
  "business_day": true,
  "session": {
    "open": "08:00:00",
    "close": "12:30:00"
  },
  "tags": [
    "special close",
    "month end"
  ]
}
```

### API versioning

There is currently only one version of the API. All endpoints are under `/v1/`.

### Reference Endpoints

These endpoints return reference data for the supported exchanges.

#### GET /exchanges

Get a list of supported exchanges' MIC codes.

Example request:

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

Path parameters:

- `mic` - MIC code of the exchange

Example request:

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

Path parameters:

- `mic` - MIC code of the exchange
- `day` - Date in ISO format (e.g., `2024-12-25`)

Example request:

```bash
curl "http://localhost:8080/v1/exchanges/XLON/days/2024-12-25"
```

Response:

```json
{
  "date": "2024-12-25",
  "name": "Christmas Day",
  "business_day": false,
  "tags": [
    "holiday"
  ]
}
```

#### GET /exchanges/{mic}/days

Get days in a date range that match criteria.

Path Parameters:

- `mic` - MIC code of the exchange

Query Parameters:

- `start` (required) - Start date in ISO format (inclusive)
- `end` (required) - End date in ISO format (inclusive)
- `business_day` (optional) - Filter to only business days (`true`) or non-business days (`false`)
- `include_tags` (optional, repeatable) - Only include days with all the given tags
- `exclude_tags` (optional, repeatable) - Exclude days with any of the given tags
- `order` (optional, default: `asc`) - Sort order: `asc` or `desc`
- `limit` (optional) - Maximum number of days to return

Example request:

```bash
curl "http://localhost:8080/v1/exchanges/XLON/days?start=2024-12-24&end=2024-12-27&business_day=false"
```

Response:

```json
[
  {
    "date": "2024-12-25",
    "name": "Christmas",
    "business_day": false,
    "tags": [
      "holiday"
    ]
  },
  {
    "date": "2024-12-26",
    "name": "Boxing Day",
    "business_day": false,
    "tags": [
      "holiday"
    ]
  }
]
```

Example request:

```bash
curl "http://localhost:8080/v1/exchanges/XLON/days?start=2024-12-24&end=2024-12-31&include_tags=special%20close&include_tags=month%20end&order=asc"
```

Response:

```json
[
  {
    "date": "2024-12-31",
    "name": "New Year's Eve",
    "business_day": true,
    "session": {
      "open": "08:00:00",
      "close": "12:30:00"
    },
    "tags": [
      "special close",
      "month end"
    ]
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
- `include_tags` (optional, repeatable) - Only include days with all the given tags
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
    "date": "2024-12-21",
    "business_day": false,
    "tags": [
      "weekend"
    ]
  },
  {
    "date": "2024-12-22",
    "business_day": false,
    "tags": [
      "weekend"
    ]
  },
  {
    "date": "2024-12-25",
    "name": "Christmas",
    "business_day": false,
    "tags": [
      "holiday"
    ]
  }
]
```

### Multi-Exchange Endpoints

These endpoints return information about one or more days for multiple exchanges in a single request.

#### GET /days/{day}

Get a specific day for multiple exchanges.

Path parameters:

- `day` - Date in ISO format (e.g., `2024-12-25`)

Query parameters:

- `mics` (required, repeatable) - One or more MIC codes of the exchanges to query

Example request:

```bash
curl "http://localhost:8080/v1/days/2024-12-25?mics=XLON&mics=XSWX"
```

Response:

```json
{
  "XLON": {
    "date": "2024-12-25",
    "name": "Christmas",
    "business_day": false,
    "tags": [
      "holiday"
    ]
  },
  "XSWX": {
    "date": "2024-12-25",
    "name": "Christmas",
    "business_day": false,
    "tags": [
      "holiday"
    ]
  }
}
```

#### GET /days

Get days in a date range that match criteria for multiple exchanges.

Query Parameters:

- `mics` (required, repeatable) - One or more MIC codes of the exchanges to query
- `start` (required) - Start date in ISO format (inclusive)
- `end` (required) - End date in ISO format (inclusive)
- `business_day` (optional) - Filter to only business days (`true`) or non-business days (`false`)
- `include_tags` (optional, repeatable) - Only include days with all the given tags
- `exclude_tags` (optional, repeatable) - Exclude days with any of the given tags
- `order` (optional, default: `asc`) - Sort order: `asc` or `desc`
- `limit` (optional) - Maximum number of date records to return (each record contains all MICs' data for that date)

The response is grouped by date, with MICs within each date ordered alphabetically.

Example request:

```bash
curl "http://localhost:8080/v1/days?start=2024-12-24&end=2024-12-27&mics=XLON&mics=XNYS&business_day=false"
```

Response:

```json
[
  {
    "XLON": {
      "date": "2024-12-25",
      "name": "Christmas",
      "business_day": false,
      "tags": [
        "holiday"
      ]
    },
    "XNYS": {
      "date": "2024-12-25",
      "name": "Christmas",
      "business_day": false,
      "tags": [
        "holiday"
      ]
    }
  },
  {
    "XLON": {
      "date": "2024-12-26",
      "name": "Boxing Day",
      "business_day": false,
      "tags": [
        "holiday"
      ]
    }
  }
]
```

Note: The `limit` parameter applies to the number of date records returned, not the total number of individual
exchange-day entries.

## Development

Clone this repository and run `uv sync` and you are good to go.

### Testing

Run the full test suite with coverage:

```bash
uv run pytest -v tests/ --cov=exchange_calendar_service
```

### Building the Docker Image

From the project root:

```bash
docker build -f docker/Dockerfile -t exchange-calendar-service .
```

### Running the Container

```bash
docker run -p 8080:8080 exchange-calendar-service
```

## License

Apache-2.0
