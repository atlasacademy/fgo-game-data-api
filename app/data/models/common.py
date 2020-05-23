from enum import Enum

from pydantic import BaseModel, BaseSettings, DirectoryPath, HttpUrl, validator


class Region(str, Enum):
    NA = "NA"
    JP = "JP"


class Settings(BaseSettings):
    na_gamedata: DirectoryPath
    jp_gamedata: DirectoryPath
    asset_url: HttpUrl
    export_all_nice: bool = False

    @validator("asset_url")
    def remove_last_slash(cls, value):
        if value.endswith("/"):
            return value[:-1]
        else:
            return value

    class Config:
        env_file = ".env"


class DetailMessage(BaseModel):
    detail: str
