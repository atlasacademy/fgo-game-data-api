from enum import Enum

from pydantic import BaseModel, BaseSettings


class Region(str, Enum):
    NA = "NA"
    JP = "JP"


class Settings(BaseSettings):
    na_gamedata: str
    jp_gamedata: str

    class Config:
        env_file = ".env"


class DetailMessage(BaseModel):
    detail: str
