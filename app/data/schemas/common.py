from typing import Optional

from pydantic import BaseModel, HttpUrl

from ..enums import Trait


class NiceTrait(BaseModel):
    id: int
    name: Trait
    negative: Optional[bool] = None


class MCAssets(BaseModel):
    male: HttpUrl
    female: HttpUrl
