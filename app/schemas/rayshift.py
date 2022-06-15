from datetime import datetime
from typing import Any, Optional

from pydantic import Field

from .base import BaseModelORJson
from .nice import DeckType


class BaseRayshiftResponse(BaseModelORJson):
    status: int
    message: str
    wait: Optional[int] = None


class DropInfo(BaseModelORJson):
    type: int
    objectId: int
    num: int
    limitCount: int
    lv: int
    rarity: int
    isRateUp: bool
    originalNum: int


class DeckSvt(BaseModelORJson):
    uniqueId: int
    name: Optional[str]
    roleType: int
    dropInfos: Optional[list[DropInfo]] = None
    npcId: int
    enemyScript: Optional[dict[str, Any]] = None
    infoScript: Optional[dict[str, Any]] = None
    index: int
    id: int
    userSvtId: int
    userSvtEquipIds: list[int]
    isFollowerSvt: bool
    npcFollowerSvtId: int


class Deck(BaseModelORJson):
    svts: list[DeckSvt]
    followerType: int
    stageId: int


class RaidInfo(BaseModelORJson):
    day: int
    uniqueId: int
    maxHp: int
    totalDamage: int


class SuperBossInfo(BaseModelORJson):
    superBossId: int
    uniqueId: int
    maxHp: int
    totalDamage: int


class UserSvt(BaseModelORJson):
    id: int
    userId: int = Field(..., title="User ID", description="Unused fields for enemies")
    svtId: int
    lv: int
    exp: int
    atk: int
    hp: int
    adjustAtk: int
    adjustHp: int
    recover: int
    chargeTurn: int
    skillId1: int
    skillId2: int
    skillId3: int
    skillLv1: int
    skillLv2: int
    skillLv3: int
    treasureDeviceId: int
    treasureDeviceLv: int
    tdRate: int
    tdAttackRate: int
    deathRate: int
    criticalRate: int
    starRate: int
    individuality: list[int]
    classPassive: list[int]
    addPassive: Optional[list[int]] = None
    aiId: int
    actPriority: int
    maxActNum: int
    displayType: int
    npcSvtType: int
    passiveSkill: Optional[list[int]] = None
    equipTargetId1: int
    equipTargetIds: Optional[list[int]] = None
    npcSvtClassId: int
    overwriteSvtId: int
    userCommandCodeIds: Optional[list[int]] = None
    commandCardParam: Optional[list[int]] = None
    afterLimitCount: Optional[int] = None
    afterIconLimitCount: Optional[int] = None
    appendPassiveSkillIds: Optional[list[int]] = None
    appendPassiveSkillLvs: Optional[list[int]] = None
    limitCount: int
    imageLimitCount: int
    dispLimitCount: int
    commandCardLimitCount: int
    iconLimitCount: int
    portraitLimitCount: int
    randomLimitCount: Optional[int] = None
    randomLimitCountSupport: Optional[int] = None
    limitCountSupport: Optional[int] = None
    battleVoice: int
    treasureDeviceLv1: int
    exceedCount: int
    status: int
    createdAt: int


class QuestDetail(BaseModelORJson):
    battleId: int
    addedTime: datetime
    region: int
    questId: int
    questPhase: int
    questSelect: int
    eventId: int
    battleType: int
    enemyDeck: list[Deck]
    transformDeck: Deck
    callDeck: list[Deck]
    shiftDeck: list[Deck]
    raidInfo: list[RaidInfo]
    startRaidInfo: list[RaidInfo]
    superBossInfo: list[SuperBossInfo]
    userSvt: list[UserSvt]


class QuestResponse(BaseModelORJson):
    questDetails: dict[int, QuestDetail]


class QuestRayshiftResponse(BaseRayshiftResponse):
    response: QuestResponse


class QuestList(BaseModelORJson):
    questId: int
    questPhase: int
    count: int
    lastUpdated: datetime
    queryIds: list[int]
    region: int


class QuestListResponse(BaseModelORJson):
    quests: list[QuestList]


class QuestListRayshiftResponse(BaseRayshiftResponse):
    response: QuestListResponse


class QuestDrop(BaseModelORJson):
    stage: int
    deckType: DeckType
    deckId: int
    npcId: int
    type: int
    objectId: int
    originalNum: int
    runs: int
    dropCount: int
    sumDropCountSquared: int
