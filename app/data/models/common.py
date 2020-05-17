from enum import Enum

from pydantic import BaseSettings


class Region(str, Enum):
    NA = "NA"
    JP = "JP"


class Settings(BaseSettings):
    na_gamedata: str
    jp_gamedata: str

    class Config:
        env_file = ".env"
