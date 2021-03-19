from typing import Any

import orjson
from pydantic import BaseModel


def orjson_dumps(v: Any, *, default: Any) -> str:
    return orjson.dumps(v, default=default, option=orjson.OPT_NON_STR_KEYS).decode()


class BaseModelORJson(BaseModel):
    """Slightly modified pydantic BaseModel that uses orjson for json methods"""

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        orm_mode = True
