import logging
from logging.handlers import HTTPHandler
from pathlib import Path
from typing import Any, Optional

import orjson
from pydantic import (
    BaseSettings,
    DirectoryPath,
    Extra,
    Field,
    HttpUrl,
    PostgresDsn,
    RedisDsn,
    SecretStr,
    validator,
)
from pydantic.main import BaseModel
from pydantic.tools import parse_obj_as
from uvicorn.logging import DefaultFormatter

from .schemas.common import Region


project_root = Path(__file__).resolve().parents[1]


class CustomHttpHandler(HTTPHandler):
    def mapLogRecord(self, record: logging.LogRecord) -> dict[str, str]:
        return {
            "username": "API",
            "content": f"API Exception\n\n```\n{self.format(record)}\n```",
        }


uvicorn_logger = logging.getLogger("uvicorn.access")
logger = logging.getLogger("fgoapi")
console_handler = logging.StreamHandler()
console_handler.setFormatter(DefaultFormatter("%(levelprefix)s %(name)s: %(message)s"))
logger.addHandler(console_handler)
logger.setLevel(uvicorn_logger.level)


def json_config_settings_source(_: BaseSettings) -> Any:
    return orjson.loads(Path("config.json").read_bytes())


class RegionSettings(BaseModel):
    gamedata: DirectoryPath
    postgresdsn: PostgresDsn


class Settings(BaseSettings):
    data: dict[Region, RegionSettings] = Field(default=...)
    redisdsn: RedisDsn = Field(default=...)
    redis_prefix: str = "fgoapi"
    clear_redis_cache: bool = True
    rayshift_api_key: SecretStr = SecretStr("")
    rayshift_api_url: HttpUrl = parse_obj_as(HttpUrl, "https://rayshift.io/api/v1/")
    quest_cache_length: int = 3600
    db_pool_size: int = 3
    db_max_overflow: int = 10
    write_postgres_data: bool = True
    write_redis_data: bool = True
    asset_url: HttpUrl = parse_obj_as(
        HttpUrl, "https://assets.atlasacademy.io/GameData/"
    )
    openapi_url: Optional[HttpUrl] = None
    export_all_nice: bool = False
    documentation_all_nice: bool = False
    github_webhook_secret: SecretStr = SecretStr("")
    github_webhook_git_pull: bool = False
    webhooks: list[str] = []
    error_webhooks: list[HttpUrl] = []

    @validator("asset_url", "rayshift_api_url")
    def remove_last_slash(cls, value: str) -> str:
        if value.endswith("/"):
            return value[:-1]
        else:
            return value

    class Config:
        extra = Extra.ignore
        env_file = ".env"
        secrets_dir = "secrets"

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):  # type: ignore
            return (
                init_settings,
                file_secret_settings,
                env_settings,
                json_config_settings_source,
            )


settings = Settings()

for url in settings.error_webhooks:
    if url.host:
        http_handler = CustomHttpHandler(
            url.host, url.path if url.path else "", method="POST", secure=True
        )
        http_handler.setLevel(logging.ERROR)
        logger.addHandler(http_handler)
