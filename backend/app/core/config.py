from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_db: str = "productos"
    postgres_user: str = "productos_app"
    postgres_password: str = ""
    database_url: str | None = None
    graphql_ide: bool = False
    log_level: str = "INFO"

    def db_url(self) -> str | URL:
        if self.database_url:
            return self.database_url
        # URL.create evita errores con @, : u otros caracteres en contraseñas.
        return URL.create(
            "postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
