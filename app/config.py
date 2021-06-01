import logging
from pathlib import Path
from typing import Optional

from pydantic import (
    BaseSettings,
    DirectoryPath,
    HttpUrl,
    PostgresDsn,
    RedisDsn,
    SecretStr,
    validator,
)
from pydantic.tools import parse_obj_as
from uvicorn.logging import DefaultFormatter


project_root = Path(__file__).resolve().parents[1]


uvicorn_logger = logging.getLogger("uvicorn.access")
logger = logging.getLogger("fgoapi")
console_handler = logging.StreamHandler()
console_handler.setFormatter(DefaultFormatter("%(levelprefix)s %(name)s: %(message)s"))
logger.addHandler(console_handler)
logger.setLevel(uvicorn_logger.level)


# pylint: disable=no-self-argument, no-self-use
class Settings(BaseSettings):
    na_gamedata: DirectoryPath
    jp_gamedata: DirectoryPath
    rayshift_api_url: HttpUrl = parse_obj_as(HttpUrl, "https://rayshift.io/api/v1/")
    quest_cache_length: int = 3600
    write_postgres_data: bool = True
    asset_url: HttpUrl = parse_obj_as(
        HttpUrl, "https://assets.atlasacademy.io/GameData/"
    )
    openapi_url: Optional[HttpUrl] = None
    export_all_nice: bool = False
    documentation_all_nice: bool = False
    github_webhook_git_pull: bool = False
    github_webhook_sleep: int = 0
    bloom_shard: Optional[int] = None
    redis_prefix: str = "fgoapi"

    @validator("asset_url", "rayshift_api_url")
    def remove_last_slash(cls, value: str) -> str:
        if value.endswith("/"):
            return value[:-1]
        else:
            return value

    class Config:
        env_file = ".env"


class SecretSettings(BaseSettings):
    na_postgresdsn: PostgresDsn
    jp_postgresdsn: PostgresDsn
    rayshift_api_key: SecretStr = SecretStr("")
    github_webhook_secret: SecretStr = SecretStr("")
    redisdsn: RedisDsn

    class Config:
        env_file = ".env"
        secrets_dir = "secrets"
