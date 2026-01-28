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


settings = Settings()
