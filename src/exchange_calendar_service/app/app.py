import importlib
import importlib.metadata
import inspect
import logging
from enum import Enum

import exchange_calendars as ec
import exchange_calendars_extensions.core as ecx_core
import fastapi
from fastapi import FastAPI

from exchange_calendar_service.core.common.cache import ExchangeCalendarCache
from exchange_calendar_service.core.common.context import Context

from .api.v1.endpoints import get_router
from .settings import Settings

log = logging.getLogger(__name__)


def _validate_and_call_init(init: object, name: str, settings: Settings) -> None:
    """Validate an init function and call it with settings."""
    if not callable(init):
        raise ValueError(f"{name} is not callable.")

    if not inspect.isfunction(init):
        raise ValueError(f"{name} is not a function.")

    if len(inspect.signature(init).parameters) != 1:
        raise ValueError(f"{name} does not have exactly one argument.")

    init(settings)


def app(_settings: Settings | None = None) -> FastAPI:
    from .settings import get_settings

    settings: Settings = _settings or get_settings()

    # If settings.init is not None, try to import it. Once imported. check if it is a callable with zero arguments.
    # If so, call it. Otherwise, raise an Exception and exit. Use importlib to import the callable.
    if settings.init:
        # Split into module and callable name.
        parts = settings.init.rsplit(":", 1)
        module_name = parts[0]
        callable_name = parts[1] if len(parts) > 1 else None

        if not callable_name:
            _ = importlib.import_module(module_name)
        else:
            # Import the module.
            module = importlib.import_module(module_name)

            # Get the callable.
            init = getattr(module, callable_name)

            _validate_and_call_init(init, settings.init, settings)

    # Discover and call entrypoints from exchange_calendar_service.init group.
    entrypoints = importlib.metadata.entry_points(
        group="exchange_calendar_service.init"
    )

    for entrypoint in entrypoints:
        log.info(f"Loading init entrypoint: {entrypoint.name}")
        init = entrypoint.load()

        _validate_and_call_init(init, f"Entrypoint {entrypoint.name}", settings)

    if settings.exchanges is None:
        settings.exchanges = tuple(
            ec.calendar_utils.get_calendar_names(include_aliases=False)
        )

    # From the contents of settings.exchanges, programmatically create dynamic Enum class with the name ExchangeEnum.
    # The MICs become both the enum member names and the enum member values.
    Exchanges: type[Enum] = Enum("ExchangeEnum", {x: x for x in settings.exchanges})

    # Apply extensions to exchange calendars.
    ecx_core.apply_extensions()

    # Initialize app context.
    _ = Context(cache=ExchangeCalendarCache(Exchanges.__members__.keys()))

    try:
        version = importlib.metadata.version("exchange_calendar_service")
    except importlib.metadata.PackageNotFoundError:
        version = "unknown"

    app = FastAPI(
        title="Exchange Calendar Service",
        version=version,
        description="A RESTful HTTP Service.",
    )

    router_v1: fastapi.APIRouter = get_router(Exchanges)

    app.include_router(router_v1, prefix="/v1")

    # if False:
    #     # The request header that should contain the API key.
    #     api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)
    #
    #     # Dependency that checks for the API key.
    #     async def get_api_key(api_key: str = Depends(api_key_header)):
    #         if api_key != settings.changes_api_key:
    #             raise HTTPException(
    #                 status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
    #             )
    #
    #     # Endpoint that requires an API key
    #     @app.post(
    #         "/update",
    #         tags=["update"],
    #         summary="Update exchange calendar changesets",
    #         dependencies=[Depends(get_api_key)],
    #     )
    #     async def update(
    #             changes_dict: ChangeSetDict = Body(
    #                 examples={
    #                     "example 1": {
    #                         "summary": "foo",
    #                         "description": "bar",
    #                         "value": {
    #                             "XNYS": {
    #                                 "add": {
    #                                     "2020-01-01": {
    #                                         "type": "holiday",
    #                                         "name": "New Year's Day",
    #                                     }
    #                                 },
    #                                 "remove": ["2020-01-01"],
    #                                 "meta": {
    #                                     "2020-01-01": {
    #                                         "tags": ["tag1", "tag2"],
    #                                         "comment": "This is a comment.",
    #                                     }
    #                                 },
    #                             }
    #                         },
    #                     }
    #                 }
    #             ),
    #     ):
    #         log.info("Received changes via endpoint.")
    #
    #         # Get currently applied changesets.
    #         changes_dict_prev: ChangeSetDict = ecx_core.get_changes_for_all_calendars()
    #
    #         if changes_dict == changes_dict_prev:
    #             log.info("No changes.")
    #             return
    #
    #         # Keys in changes_dict but not in changes_dict_prev.
    #         keys_to_add = set(changes_dict.keys()) - set(changes_dict_prev.keys())
    #
    #         # Keys in both changes and changes_prev.
    #         keys_to_update = set(changes_dict.keys()) & set(changes_dict_prev.keys())
    #
    #         # Keys in changes_prev but not in changes.
    #         keys_to_remove = set(changes_dict_prev.keys()) - set(changes_dict.keys())
    #
    #         # Reset all calendars.
    #         ecx_core.reset_all_calendars()
    #
    #         # Apply change sets.
    #         for key in keys_to_add:
    #             log.info(f"Adding new changes for exchange {key}:")
    #             log_iterable(
    #                 log,
    #                 [
    #                     " + " + line
    #                     for line in changes_dict[key]
    #                 .model_dump_json(indent=2)
    #                 .split("\n")
    #                 ],
    #                 logging.INFO,
    #             )
    #             ecx_core.update_calendar(key, dict(changes_dict[key]))
    #
    #         # Update existing change sets.
    #         for key in keys_to_update:
    #             action2str = {
    #                 "k": " ",
    #                 "i": "+",
    #                 "r": "-",
    #                 "o": ".",
    #             }
    #             if changes_dict[key] == changes_dict_prev[key]:
    #                 log.info(f"Changes remain the same for exchange {key}:")
    #                 log_iterable(
    #                     log,
    #                     [
    #                         "   " + line
    #                         for line in changes_dict[key]
    #                     .model_dump_json(indent=2)
    #                     .split("\n")
    #                     ],
    #                     logging.INFO,
    #                 )
    #             else:
    #                 log.info(f"Updating changes for exchange {key}:")
    #                 diff = myers.diff(
    #                     a=changes_dict_prev[key].model_dump_json(indent=2).split("\n"),
    #                     b=changes_dict[key].model_dump_json(indent=2).split("\n"),
    #                 )
    #                 diff = [
    #                     " " + action2str[action] + " " + line for action, line in diff
    #                 ]
    #                 log_iterable(log, diff, logging.INFO)
    #
    #             ecx_core.update_calendar(key, dict(changes_dict[key]))
    #
    #         # Remove change sets.
    #         for key in keys_to_remove:
    #             log.info(f"Removing changes for exchange {key}:")
    #             log_iterable(
    #                 log,
    #                 [
    #                     " - " + line
    #                     for line in changes_dict_prev[key]
    #                 .model_dump_json(indent=2)
    #                 .split("\n")
    #                 ],
    #                 logging.INFO,
    #             )
    #
    #         # Refresh all affected calendars in cache.
    #         for key in keys_to_add | keys_to_update | keys_to_remove:
    #             Context().cache.refresh(key)

    return app
