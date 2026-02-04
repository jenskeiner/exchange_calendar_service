from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="EXCHANGE_CALENDAR_SERVICE_",
        env_nested_delimiter="__",
        env_file=".env",
    )

    # The optional full name of a callable.
    init: str | None = None

    # The available exchanges.
    exchanges: tuple[str, ...] | None = None


_instance: Settings | None = None


def get_settings() -> Settings:
    """Get the current settings instance."""
    global _instance
    if _instance is None:
        _instance = Settings()
    return _instance


def set_settings(settings: Settings | None) -> None:
    """Set a new settings instance (primarily for testing)."""
    global _instance
    _instance = settings
