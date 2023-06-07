from dataclasses import dataclass
from typing import Any, Iterable

from sqlalchemy.ext.asyncio import AsyncConnection

from ...config import Settings
from ...schemas.common import Language, Region
from ...schemas.gameenums import CARD_TYPE_NAME, NiceTdEffectFlag
from ...schemas.nice import AssetURL, NiceTd, NiceTdSvt
from ...schemas.raw import (
    MstSvtTreasureDevice,
    MstSvtTreasureDeviceRelease,
    TdEntityNoReverse,
)
from ..raw import get_td_entity_no_reverse, get_td_entity_no_reverse_many
from ..utils import get_np_name, get_traits_list, strip_formatting_brackets
from .func import get_nice_function
from .skill import get_nice_skill_release, get_nice_skill_script


settings = Settings()


def get_nice_td_svt(
    td_svt: MstSvtTreasureDevice, td_releases: list[MstSvtTreasureDeviceRelease]
) -> NiceTdSvt:
    return NiceTdSvt(
        svtId=td_svt.svtId,
        num=td_svt.num,
        priority=td_svt.priority,
        damage=td_svt.damage,
        strengthStatus=td_svt.strengthStatus,
        flag=td_svt.flag,
        imageIndex=td_svt.imageIndex,
        condQuestId=td_svt.condQuestId,
        condQuestPhase=td_svt.condQuestPhase,
        condLv=td_svt.condLv,
        condFriendshipRank=td_svt.condFriendshipRank,
        motion=td_svt.motion,
        card=CARD_TYPE_NAME[td_svt.cardId],
        releaseConditions=[
            get_nice_skill_release(release)
            for release in td_releases
            if (release.svtId, release.num, release.priority)
            == (td_svt.svtId, td_svt.num, td_svt.priority)
        ],
    )


def get_nice_td_effect_flag(effectFlag: int) -> NiceTdEffectFlag:
    if effectFlag == 1:
        return NiceTdEffectFlag.attackEnemyAll
    elif effectFlag == 2:
        return NiceTdEffectFlag.attackEnemyOne

    return NiceTdEffectFlag.support


async def get_nice_td(
    conn: AsyncConnection,
    tdEntity: TdEntityNoReverse,
    svtId: int,
    region: Region,
    lang: Language,
) -> list[dict[str, Any]]:
    sorted_svtTd = sorted(
        tdEntity.mstSvtTreasureDevice, key=lambda x: (x.svtId, x.num, -x.priority)
    )

    nice_td: dict[str, Any] = {
        "id": tdEntity.mstTreasureDevice.id,
        "name": get_np_name(
            tdEntity.mstTreasureDevice.name, tdEntity.mstTreasureDevice.ruby, lang
        ),
        "originalName": tdEntity.mstTreasureDevice.name,
        "ruby": tdEntity.mstTreasureDevice.ruby,
        "rank": tdEntity.mstTreasureDevice.rank,
        "type": tdEntity.mstTreasureDevice.typeText,
        "effectFlags": [get_nice_td_effect_flag(tdEntity.mstTreasureDevice.effectFlag)],
        "individuality": get_traits_list(tdEntity.mstTreasureDevice.individuality),
        "npSvts": [
            get_nice_td_svt(td_svt, tdEntity.mstSvtTreasureDeviceRelease)
            for td_svt in sorted_svtTd
            if svtId == -1 or td_svt.svtId == svtId
        ],
    }

    if tdEntity.mstTreasureDeviceDetail:
        nice_td["detail"] = strip_formatting_brackets(
            tdEntity.mstTreasureDeviceDetail[0].detail
        )
        nice_td["unmodifiedDetail"] = tdEntity.mstTreasureDeviceDetail[0].detail

    nice_td["npGain"] = {
        "buster": [td_lv.tdPointB for td_lv in tdEntity.mstTreasureDeviceLv],
        "arts": [td_lv.tdPointA for td_lv in tdEntity.mstTreasureDeviceLv],
        "quick": [td_lv.tdPointQ for td_lv in tdEntity.mstTreasureDeviceLv],
        "extra": [td_lv.tdPointEx for td_lv in tdEntity.mstTreasureDeviceLv],
        "np": [td_lv.tdPoint for td_lv in tdEntity.mstTreasureDeviceLv],
        "defence": [td_lv.tdPointDef for td_lv in tdEntity.mstTreasureDeviceLv],
    }

    nice_td["script"] = {}
    if tdEntity.mstTreasureDeviceLv[0].script:
        for script_key in tdEntity.mstTreasureDeviceLv[0].script:
            nice_td["script"][script_key] = [
                get_nice_skill_script(tdLv.script)[script_key] if tdLv.script else None
                for tdLv in tdEntity.mstTreasureDeviceLv
            ]
    for script_key in ("tdTypeChangeIDs", "excludeTdChangeTypes"):
        if script_key in tdEntity.mstTreasureDevice.script:
            nice_td["script"][script_key] = tdEntity.mstTreasureDevice.script[
                script_key
            ]

    nice_td["functions"] = []

    for funci, _ in enumerate(tdEntity.mstTreasureDeviceLv[0].funcId):
        if tdEntity.mstTreasureDeviceLv[0].expandedFuncId:
            nice_func = await get_nice_function(
                conn,
                region,
                tdEntity.mstTreasureDeviceLv[0].expandedFuncId[funci],
                svals=[
                    skill_lv.svals[funci] for skill_lv in tdEntity.mstTreasureDeviceLv
                ],
                svals2=[
                    skill_lv.svals2[funci] for skill_lv in tdEntity.mstTreasureDeviceLv
                ],
                svals3=[
                    skill_lv.svals3[funci] for skill_lv in tdEntity.mstTreasureDeviceLv
                ],
                svals4=[
                    skill_lv.svals4[funci] for skill_lv in tdEntity.mstTreasureDeviceLv
                ],
                svals5=[
                    skill_lv.svals5[funci] for skill_lv in tdEntity.mstTreasureDeviceLv
                ],
            )

            nice_td["functions"].append(nice_func)

    chosen_svts = [svt_td for svt_td in sorted_svtTd if svt_td.svtId == svtId]

    base_settings_id = {
        "base_url": settings.asset_url,
        "region": region,
        "item_id": svtId,
    }

    if not chosen_svts and not sorted_svtTd:  # pragma: no cover
        base_settings_id["item_id"] = tdEntity.mstTreasureDevice.id
        nice_td |= {
            "svtId": tdEntity.mstTreasureDevice.id,
            "icon": AssetURL.commands.format(**base_settings_id, i="np"),
            "strengthStatus": 0,
            "num": 0,
            "priority": 0,
            "condQuestId": 0,
            "condQuestPhase": 0,
            "card": CARD_TYPE_NAME[5],
            "npDistribution": [],
            "releaseConditions": [],
        }
    else:
        if chosen_svts:
            chosen_svt = chosen_svts[0]
        else:
            chosen_svt = sorted_svtTd[0]

        if svtId == -1:
            base_settings_id["item_id"] = chosen_svt.svtId

        imageId = chosen_svt.imageIndex
        if imageId < 2:
            file_i = "np"
        else:
            file_i = "np" + str(imageId // 2)
        nice_td |= {
            "svtId": chosen_svt.svtId,
            "icon": AssetURL.commands.format(**base_settings_id, i=file_i),
            "strengthStatus": chosen_svt.strengthStatus,
            "num": chosen_svt.num,
            "priority": chosen_svt.priority,
            "condQuestId": chosen_svt.condQuestId,
            "condQuestPhase": chosen_svt.condQuestPhase,
            "card": CARD_TYPE_NAME[chosen_svt.cardId],
            "npDistribution": chosen_svt.damage,
            "releaseConditions": [
                get_nice_skill_release(release)
                for release in tdEntity.mstSvtTreasureDeviceRelease
                if (release.svtId, release.num, release.priority)
                == (chosen_svt.svtId, chosen_svt.num, chosen_svt.priority)
            ],
        }

    return [nice_td]


async def get_nice_td_from_id(
    conn: AsyncConnection,
    region: Region,
    td_id: int,
    lang: Language,
) -> NiceTd:
    raw_td = await get_td_entity_no_reverse(conn, td_id, expand=True)

    nice_td = NiceTd.parse_obj((await get_nice_td(conn, raw_td, -1, region, lang))[0])

    return nice_td


@dataclass(eq=True, frozen=True)
class TdSvt:
    """Required parameters to get a specific nice NP"""

    td_id: int
    svt_id: int


MultipleNiceTds = dict[TdSvt, NiceTd]


async def get_multiple_nice_tds(
    conn: AsyncConnection, region: Region, td_svts: Iterable[TdSvt], lang: Language
) -> MultipleNiceTds:
    """Get multiple nice NPs at once

    Args:
        `conn`: DB Connection
        `region`: Region
        `td_svts`: List of skill id - NP id tuple pairs

    Returns:
        Mapping of td id - svt id tuple to nice NP
    """
    raw_tds = {
        td.mstTreasureDevice.id: td
        for td in await get_td_entity_no_reverse_many(
            conn, [td_svt.td_id for td_svt in td_svts], expand=True
        )
    }
    return {
        td_svt: NiceTd.parse_obj(
            (
                await get_nice_td(
                    conn, raw_tds[td_svt.td_id], td_svt.svt_id, region, lang
                )
            )[0]
        )
        for td_svt in td_svts
        if td_svt.td_id in raw_tds
    }
