from typing import Optional

from pydantic import BaseModel, HttpUrl

from ..enums import NiceSvtType, SvtClass


class BasicFunction(BaseModel):
    funcId: int
    # funcType: Union[NiceFuncType, int]
    # funcTargetType: Union[NiceFuncTargetType, int]
    # funcTargetTeam: Union[FuncApplyTarget, int]
    # funcPopupText: str
    # funcPopupIcon: Optional[HttpUrl] = None
    # functvals: List[NiceTrait]
    # funcquestTvals: List[NiceTrait]
    # traitVals: List[NiceTrait] = []
    # buffs: List[NiceBuff]


class BasicSkill(BaseModel):
    id: int
    name: str
    icon: Optional[HttpUrl] = None


class BasicTd(BaseModel):
    id: int
    name: str
    icon: Optional[HttpUrl] = None


class BasicServant(BaseModel):
    id: int
    collectionNo: int
    name: str
    type: NiceSvtType
    className: SvtClass
    rarity: int
    face: HttpUrl


class BasicEquip(BaseModel):
    id: int
    collectionNo: int
    name: str
    rarity: int
    face: HttpUrl
