from typing import Optional

from pydantic import BaseModel, HttpUrl

from ..enums import Trait


class NiceTrait(BaseModel):
    """Nice trait"""

    id: int
    name: Trait
    negative: Optional[bool] = None


class MCAssets(BaseModel):
    """Mystic Code Assets"""

    male: HttpUrl
    female: HttpUrl
