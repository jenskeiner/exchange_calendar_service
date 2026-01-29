from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="EXCHANGE_CALENDAR_SERVICE_",
        env_nested_delimiter="__",
        env_file=".env",
    )

    changes_api_key: str | None = None

    # The optional full name of callable.
    init: str | None = None

    # The available exchanges.
    exchanges: dict[str, str] | None = None


_instance: Settings | None = None


def get_settings(create: bool = True) -> Settings | None:
    """Get the current settings instance."""
    global _instance
    if _instance is None and create:
        _instance = Settings()
    return _instance


def set_settings(settings: Settings | None) -> None:
    """Set a new settings instance (primarily for testing)."""
    global _instance
    _instance = settings
