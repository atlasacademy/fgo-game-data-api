import logging

from pydantic import BaseSettings, DirectoryPath, HttpUrl, SecretStr, validator


uvicorn_logger = logging.getLogger("uvicorn.access")
logger = logging.getLogger("fgoapi")
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(levelname)-9s %(name)s: %(message)s"))
logger.addHandler(console_handler)
logger.setLevel(uvicorn_logger.level)


# pylint: disable=no-self-argument, no-self-use
class Settings(BaseSettings):
    na_gamedata: DirectoryPath
    jp_gamedata: DirectoryPath
    asset_url: HttpUrl
    export_all_nice: bool = False
    documentation_all_nice: bool = False
    lru_cache_size: int = 128
    github_webhook_secret: SecretStr = SecretStr("")
    github_webhook_git_pull: bool = False
    github_webhook_sleep: int = 0

    @validator("asset_url")
    def remove_last_slash(cls, value: str) -> str:
        if value.endswith("/"):
            return value[:-1]
        else:
            return value

    class Config:
        env_file = ".env"
