from pydantic import BaseModel, HttpUrl

from ..enums import Trait


class NiceTrait(BaseModel):
    id: int
    name: Trait


class MCAssets(BaseModel):
    male: HttpUrl
    female: HttpUrl
