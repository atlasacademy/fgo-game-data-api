from pydantic import BaseSettings, DirectoryPath, HttpUrl, validator


class Settings(BaseSettings):
    na_gamedata: DirectoryPath
    jp_gamedata: DirectoryPath
    asset_url: HttpUrl
    export_all_nice: bool = False
    documentation_all_nice: bool = False
    nice_servant_lru_cache: bool = False
    github_webhook_secret: str = ""
    github_webhook_sleep: int = 0

    @validator("asset_url")
    def remove_last_slash(cls, value):
        if value.endswith("/"):
            return value[:-1]
        else:
            return value

    class Config:
        env_file = ".env"
