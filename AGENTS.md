# Exchange Calendar Service

A library and an HTTP web service based
on [exchange_calendars_extensions](https://github.com/jenskeiner/exchange_calendars_extensions) to query exchange
calendars.

## Build/Run

Starting the web service app in the foreground, listening on http://localhost:8080:

```bash
uv run python -m exchange_calendar_service
```

## Config

Configuration of the app is done via [Settings](src/exchange_calendar_service/app/settings.py), a Pydantic Settings.

Prefer setting environment variables when running the app to change defaults settings:

- EXCHANGE_CALENDAR_SERVICE_CHANGES_API_KEY: Optional API key. If set, enables the Changes API through which changes to
  calendars can be injected.
- EXCHANGE_CALENDAR_SERVICE_INIT: Optional init function. If set, must be a string pointing to a callable, e.g.
  `customize:init`, that will be called when the app starts up. Can be used to modify existing calendars or to add new
  ones.
- EXCHANGE_CALENDAR_SERVICE_EXCHANGES: Optional list/tuple of supported exchange MICs. If set, must be a JSON array
  of MIC codes, e.g. ["XLON", "XNYS"]. Default is to use all exchange calendars.

### Init Functions

Init functions can be provided via two mechanisms:

1. **Environment variable** (`EXCHANGE_CALENDAR_SERVICE_INIT`): Points to a single callable in `module:callable` format.
2. **Entry points** (`exchange_calendar_service.init` group): All discovered entrypoints are automatically called on
   startup. Allows customization via installed packages without environment variables.

Both mechanisms can be used together - the environment variable callable (if set) is called first, followed by all
discovered entrypoints.

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
- Prefer immutable collections (e.g. tuples) over mutable ones (e.g. lists) where possible.

## Testing

```bash
uv run pytest -v tests/ --cov=exchange_calendar_service --cov-fail-under=80
```

Coverage gate: 80% minimum.
