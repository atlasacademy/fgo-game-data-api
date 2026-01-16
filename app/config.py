from pathlib import Path
from typing import Any, Optional, Type

from git import Repo
from pydantic import (
    DirectoryPath,
    Field,
    HttpUrl,
    PostgresDsn,
    RedisDsn,
    SecretStr,
    field_validator,
)
from pydantic.main import BaseModel
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
)

from .schemas.common import Region, RepoInfo

project_root = Path(__file__).resolve().parents[1]


class RegionSettings(BaseModel):
    gamedata: DirectoryPath
    postgresdsn: PostgresDsn


class Settings(BaseSettings):
    data: dict[Region, RegionSettings] = Field(default=...)
    redisdsn: RedisDsn = Field(default=...)
    redis_prefix: str = "fgoapi"
    clear_redis_cache: bool = True
    rayshift_api_key: SecretStr = SecretStr("")
    rayshift_api_url: str = "https://rayshift.io/api/v1/"
    quest_cache_length: int = 3600
    db_pool_size: int = 3
    db_max_overflow: int = 10
    write_postgres_data: bool = True
    write_redis_data: bool = True
    asset_url: str = "https://assets.atlasacademy.io/GameData"
    openapi_url: Optional[HttpUrl] = None
    export_all_nice: bool = False
    documentation_all_nice: bool = False
    github_webhook_secret: SecretStr = SecretStr("")
    github_webhook_git_pull: bool = False
    webhooks: list[str] = []
    error_webhooks: list[HttpUrl] = []
    quest_heavy_cache_threshold: int = 1000

    @field_validator("asset_url", "rayshift_api_url")
    @classmethod
    def remove_last_slash(cls, value: str) -> str:
        return value.removesuffix("/")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            file_secret_settings,
            env_settings,
            dotenv_settings,
            JsonConfigSettingsSource(
                settings_cls, json_file=Path("config.json"), json_file_encoding="utf-8"
            ),
        )


def get_repo_info(loc: Path) -> RepoInfo:
    repo = Repo(loc)
    latest_commit = repo.commit()
    return RepoInfo(
        hash=latest_commit.hexsha[:6],
        timestamp=latest_commit.committed_date,
    )


def get_app_info() -> RepoInfo:
    return get_repo_info(project_root)


def get_instance_info(settings: Settings) -> dict[str, Any]:
    app_info = get_app_info()
    return {
        "app_version": app_info.model_dump(mode="json"),
        "app_settings": settings.model_dump(mode="json"),
        "file_path": str(project_root),
    }


EXTRA_SVT_ID_IN_NICE = (600710, 2501500)
