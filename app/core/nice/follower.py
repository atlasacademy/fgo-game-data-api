import asyncio
from dataclasses import dataclass

import orjson
from sqlalchemy.ext.asyncio import AsyncConnection

from ...core.basic import (
    BasicServantGet,
    get_basic_servant,
    get_multiple_basic_servants,
)
from ...core.utils import get_flags, get_nice_trait
from ...redis import Redis
from ...schemas.basic import BasicServant
from ...schemas.common import Language, NiceTrait, Region
from ...schemas.gameenums import COND_TYPE_NAME, NPC_SERVANT_FOLLOWER_FLAG_NAME
from ...schemas.nice import (
    EnemySkill,
    NiceEquip,
    NpcServant,
    SupportServant,
    SupportServantEquip,
    SupportServantLimit,
    SupportServantMisc,
    SupportServantRelease,
    SupportServantScript,
    SupportServantTd,
)
from ...schemas.raw import NpcFollower, NpcFollowerRelease, NpcSvtEquip, NpcSvtFollower
from .nice import get_nice_equip_model
from .skill import MultipleNiceSkills, SkillSvt, get_multiple_nice_skills
from .td import MultipleNiceTds, TdSvt, get_multiple_nice_tds


def get_nice_follower_release(
    npcFollowerRelease: NpcFollowerRelease,
) -> SupportServantRelease:
    return SupportServantRelease(
        type=COND_TYPE_NAME[npcFollowerRelease.condType],
        targetId=npcFollowerRelease.condTargetId,
        value=npcFollowerRelease.condValue,
    )


def get_nice_follower_traits(followerIndividuality: str) -> list[NiceTrait]:
    if followerIndividuality == "NONE":
        return []

    return [get_nice_trait(trait) for trait in orjson.loads(followerIndividuality)]


def get_nice_follower_skills(
    svt: NpcSvtFollower, all_skills: MultipleNiceSkills
) -> EnemySkill:
    return EnemySkill(
        skillId1=svt.skillId1,
        skillId2=svt.skillId2,
        skillId3=svt.skillId3,
        skill1=all_skills.get(SkillSvt(svt.skillId1, svt.svtId), None),
        skill2=all_skills.get(SkillSvt(svt.skillId2, svt.svtId), None),
        skill3=all_skills.get(SkillSvt(svt.skillId3, svt.svtId), None),
        skillLv1=svt.skillLv1,
        skillLv2=svt.skillLv2,
        skillLv3=svt.skillLv3,
    )


def get_nice_follower_td(
    svt: NpcSvtFollower, all_nps: MultipleNiceTds
) -> SupportServantTd:
    return SupportServantTd(
        noblePhantasmId=svt.treasureDeviceId,
        noblePhantasm=all_nps.get(TdSvt(svt.treasureDeviceId, svt.svtId), None),
        noblePhantasmLv=svt.treasureDeviceLv,
    )


def get_nice_follower_limit(npcSvtFollower: NpcSvtFollower) -> SupportServantLimit:
    return SupportServantLimit(limitCount=npcSvtFollower.limitCount)


def get_nice_follower_equip(
    npcSvtEquip: NpcSvtEquip, all_equips: dict[int, NiceEquip]
) -> SupportServantEquip:
    return SupportServantEquip(
        equip=all_equips[npcSvtEquip.svtId],
        lv=npcSvtEquip.lv,
        limitCount=npcSvtEquip.limitCount,
    )


def get_nice_follower_misc(
    npcFollower: NpcFollower, npcSvtFollower: NpcSvtFollower
) -> SupportServantMisc:
    return SupportServantMisc(
        followerFlag=npcFollower.flag,
        svtFollowerFlag=npcSvtFollower.flag,
    )


def get_nice_follower_script(npcScript: str) -> SupportServantScript:
    script = SupportServantScript()
    try:
        parsed = orjson.loads(npcScript)

        if "dispLimitCount" in parsed:
            script.dispLimitCount = int(parsed["dispLimitCount"])
        if "eventDeckIndex" in parsed:
            script.eventDeckIndex = int(parsed["eventDeckIndex"])
    except orjson.JSONDecodeError:  # pragma: no cover
        pass

    return script


def get_npc_disp_limit(npcFollower: NpcFollower, npcSvtFollower: NpcSvtFollower) -> int:
    npcScript = get_nice_follower_script(npcFollower.npcScript)
    return (
        npcScript.dispLimitCount
        if npcScript.dispLimitCount
        else npcSvtFollower.limitCount
    )


async def get_nice_npc_servant(
    redis: Redis,
    region: Region,
    npcSvtFollower: NpcSvtFollower,
    all_skills: MultipleNiceSkills,
    all_tds: MultipleNiceTds,
    lang: Language,
) -> NpcServant:
    return NpcServant(
        npcId=npcSvtFollower.id,
        name=npcSvtFollower.name,
        svt=await get_basic_servant(
            redis,
            region,
            npcSvtFollower.svtId,
            svt_limit=npcSvtFollower.limitCount,
            lang=lang,
        ),
        lv=npcSvtFollower.lv,
        atk=npcSvtFollower.atk,
        hp=npcSvtFollower.hp,
        traits=get_nice_follower_traits(npcSvtFollower.individuality),
        skills=get_nice_follower_skills(npcSvtFollower, all_skills),
        noblePhantasm=get_nice_follower_td(npcSvtFollower, all_tds),
        limit=get_nice_follower_limit(npcSvtFollower),
        flags=get_flags(npcSvtFollower.flag, NPC_SERVANT_FOLLOWER_FLAG_NAME),
    )


def get_nice_support_servant(
    npcFollower: NpcFollower,
    basic_svt: BasicServant,
    npcFollowerRelease: list[NpcFollowerRelease],
    npcSvtFollower: NpcSvtFollower,
    npcSvtEquip: list[NpcSvtEquip],
    all_skills: MultipleNiceSkills,
    all_tds: MultipleNiceTds,
    all_equips: dict[int, NiceEquip],
) -> SupportServant:
    return SupportServant(
        id=npcFollower.id,
        npcSvtFollowerId=npcSvtFollower.id,
        priority=npcFollower.priority,
        name=npcSvtFollower.name,
        svt=basic_svt,
        releaseConditions=[
            get_nice_follower_release(release) for release in npcFollowerRelease
        ],
        lv=npcSvtFollower.lv,
        atk=npcSvtFollower.atk,
        hp=npcSvtFollower.hp,
        traits=get_nice_follower_traits(npcSvtFollower.individuality),
        skills=get_nice_follower_skills(npcSvtFollower, all_skills),
        noblePhantasm=get_nice_follower_td(npcSvtFollower, all_tds),
        flags=get_flags(npcSvtFollower.flag, NPC_SERVANT_FOLLOWER_FLAG_NAME),
        equips=[get_nice_follower_equip(equip, all_equips) for equip in npcSvtEquip],
        script=get_nice_follower_script(npcFollower.npcScript),
        limit=get_nice_follower_limit(npcSvtFollower),
        misc=get_nice_follower_misc(npcFollower, npcSvtFollower),
    )


@dataclass
class NiceNpc:
    support_servants: list[SupportServant]
    ai_npc: dict[int, NpcServant]


async def get_nice_support_servants(
    conn: AsyncConnection,
    redis: Redis,
    region: Region,
    npcFollower: list[NpcFollower],
    npcFollowerRelease: list[NpcFollowerRelease],
    npcSvtFollower: list[NpcSvtFollower],
    npcSvtEquip: list[NpcSvtEquip],
    lang: Language,
    aiNpcIds: list[int] | None = None,
) -> NiceNpc:
    all_skill_ids: set[SkillSvt] = set()
    all_td_ids: set[TdSvt] = set()
    for npcSvt in npcSvtFollower:
        if npcSvt.treasureDeviceId != 0:
            all_td_ids.add(TdSvt(npcSvt.treasureDeviceId, npcSvt.svtId))
        for skill_id in [
            npcSvt.skillId1,
            npcSvt.skillId2,
            npcSvt.skillId3,
        ]:
            if skill_id != 0:
                all_skill_ids.add(SkillSvt(skill_id, npcSvt.svtId))

    svt_follower_map = {
        svt_follower.id: svt_follower for svt_follower in npcSvtFollower
    }

    all_svt_ids = [
        BasicServantGet(
            svt_follower_map[npc.leaderSvtId].svtId,
            svt_follower_map[npc.leaderSvtId].limitCount,
            get_npc_disp_limit(npc, svt_follower_map[npc.leaderSvtId]),
        )
        for npc in npcFollower
    ]

    all_skills, all_tds, all_svts = await asyncio.gather(
        get_multiple_nice_skills(conn, region, all_skill_ids, lang),
        get_multiple_nice_tds(conn, region, all_td_ids, lang),
        get_multiple_basic_servants(redis, region, all_svt_ids, lang),
    )

    all_equip_ids = {equip.svtId for equip in npcSvtEquip}
    all_equips = {
        equip_id: await get_nice_equip_model(conn, region, equip_id, lang, lore=False)
        for equip_id in all_equip_ids
    }

    out_support_servants: list[SupportServant] = []
    for i, npc in enumerate(npcFollower):
        svt_follower = svt_follower_map[npc.leaderSvtId]
        follower_release = [rel for rel in npcFollowerRelease if rel.id == npc.id]
        svt_equip = [equip for equip in npcSvtEquip if equip.id in npc.svtEquipIds]
        basic_svt = all_svts[i]

        nice_support_servant = get_nice_support_servant(
            npcFollower=npc,
            basic_svt=basic_svt,
            npcFollowerRelease=follower_release,
            npcSvtFollower=svt_follower,
            npcSvtEquip=svt_equip,
            all_skills=all_skills,
            all_tds=all_tds,
            all_equips=all_equips,
        )
        out_support_servants.append(nice_support_servant)

    if aiNpcIds:
        ai_npc = {
            aiNpcId: await get_nice_npc_servant(
                redis=redis,
                region=region,
                npcSvtFollower=next(
                    npc_svt for npc_svt in npcSvtFollower if npc_svt.id == aiNpcId
                ),
                all_skills=all_skills,
                all_tds=all_tds,
                lang=lang,
            )
            for aiNpcId in aiNpcIds
        }
    else:
        ai_npc = {}

    return NiceNpc(support_servants=out_support_servants, ai_npc=ai_npc)
