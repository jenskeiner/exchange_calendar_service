# Exchange Calendar Service

A library and an HTTP web service based
on [exchange_calendars_extensions](https://github.com/jenskeiner/exchange_calendars_extensions) to query exchange
calendars.

## Build/Run

Starting the web service app in the foreground, listening on http://localhost:8080:

```bash
uv run python -m exchange_calendar_service.app
```

## Config

Configuration of the app is done via [Settings](src/exchange_calendar_service/app/settings.py), a a Pydantic Settings.

Prefer setting environment variables when running the app to change defaults settings:

- EXCHANGE_CALENDAR_SERVICE_CHANGES_API_KEY: Optional API key. If set, enables the Changes API through which changes to
  calendars can be injected.
- EXCHANGE_CALENDAR_SERVICE_INIT: Optional init function. If set, must be a string pointing to a callable, e.g.
  `customize:init`. that will be called when the app starts up. Can be used to modify existing calendars or to add new
  ones.
- EXCHANGE_CALENDAR_SERVICE_EXCHANGES: Optional dictionary of supported exchanges. If set, must be a dictionary of
  string mapping to strings. Used to build an enum class of supported exchanges. Keys become enum member names, values
  become enum member values and must be valid exchange calendar names, e.g. {"XLON": "XLON"}. Default is to use all
  exchange calendars.

## Conventions

- Python 3.12+, type hints required everywhere
- When making changes:
    - make code changes
    - run all tests
    - fix issues iteratively until all pass
    - update any related documentation, i.e. this file and README.md, where necessary.
- Comments only for non-obvious logic
- Pydantic for config/data classes
- `gh` CLI for GitHub auth (no separate token)
- Avoid using @dataclass, use Pydantic instead
- Test are grouped into files matching the directory structure of the code unde rtest.
- Test classes group tests that are related to the same functionality.

## Testing

```bash
uv run pytest -v tests/ --cov=exchange_calendar_service --cov-fail-under=80
```

Coverage gate: 80% minimum.
