from ....schemas.enums import (
    SERVANT_PERSONALITY_NAME,
    SERVANT_POLICY_NAME,
    ServantPersonality,
    ServantPolicy,
)
from ....schemas.gameenums import STATUS_RANK_NAME, NiceStatusRank
from ....schemas.nice import NiceSvtLimit
from ....schemas.raw import MstSvtLimit


def get_nice_status_rank(rank_number: int) -> NiceStatusRank:
    return STATUS_RANK_NAME.get(rank_number, NiceStatusRank.unknown)


def get_nice_svt_limit(limit: MstSvtLimit) -> NiceSvtLimit:
    return NiceSvtLimit(
        limitCount=limit.limitCount,
        rarity=limit.rarity,
        lvMax=limit.lvMax,
        hpBase=limit.hpBase,
        hpMax=limit.hpMax,
        atkBase=limit.atkBase,
        atkMax=limit.atkMax,
        criticalWeight=limit.criticalWeight,
        strength=get_nice_status_rank(limit.power),
        endurance=get_nice_status_rank(limit.defense),
        agility=get_nice_status_rank(limit.agility),
        magic=get_nice_status_rank(limit.magic),
        luck=get_nice_status_rank(limit.luck),
        np=get_nice_status_rank(limit.treasureDevice),
        deity=get_nice_status_rank(limit.deity),
        policy=SERVANT_POLICY_NAME.get(limit.policy, ServantPolicy.unknown),
        personality=SERVANT_PERSONALITY_NAME.get(
            limit.personality, ServantPersonality.unknown
        ),
    )
