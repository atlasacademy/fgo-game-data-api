from typing import Optional

from sqlalchemy.ext.asyncio import AsyncConnection

from ...config import Settings
from ...schemas.common import Language, MCAssets, Region
from ...schemas.nice import (
    AssetURL,
    ExtraMCAssets,
    NiceMysticCode,
    NiceMysticCodeCostume,
    NiceSkill,
)
from ...schemas.raw import MstCommonRelease, MstEquip, MstEquipAdd
from .. import raw
from ..utils import fmt_url, get_translation
from .common_release import get_nice_common_release
from .skill import get_nice_skill_with_svt


settings = Settings()


def get_nice_mc_costume(
    region: Region,
    equip: MstEquip,
    equipAdd: MstEquipAdd,
    releases: list[MstCommonRelease],
) -> NiceMysticCodeCostume:
    base_settings = {"base_url": settings.asset_url, "region": region}
    extraAssets = ExtraMCAssets(
        item=MCAssets(
            male=fmt_url(
                AssetURL.mc["item"], **base_settings, item_id=equip.maleImageId
            ),
            female=fmt_url(
                AssetURL.mc["item"], **base_settings, item_id=equip.femaleImageId
            ),
        ),
        masterFigure=MCAssets(
            male=fmt_url(
                AssetURL.mc["masterFigure"],
                **base_settings,
                item_id=equipAdd.maleImageId,
            ),
            female=fmt_url(
                AssetURL.mc["masterFigure"],
                **base_settings,
                item_id=equipAdd.femaleImageId,
            ),
        ),
        masterFace=MCAssets(
            male=fmt_url(
                AssetURL.mc["masterFaceImage"],
                **base_settings,
                item_id=equipAdd.maleImageId,
            ),
            female=fmt_url(
                AssetURL.mc["masterFaceImage"],
                **base_settings,
                item_id=equipAdd.femaleImageId,
            ),
        ),
    )

    return NiceMysticCodeCostume(
        id=equipAdd.id,
        releaseConditions=[
            get_nice_common_release(release)
            for release in releases
            if release.id == equipAdd.commonReleaseId
        ],
        extraAssets=extraAssets,
    )


async def get_nice_mystic_code(
    conn: AsyncConnection,
    region: Region,
    mc_id: int,
    lang: Language,
    mstCc: Optional[MstEquip] = None,
) -> NiceMysticCode:
    raw_mc = await raw.get_mystic_code_entity(conn, mc_id, True, mstCc)
    base_settings = {"base_url": settings.asset_url, "region": region}
    nice_mc = NiceMysticCode(
        id=raw_mc.mstEquip.id,
        name=get_translation(lang, raw_mc.mstEquip.name),
        shortName=raw_mc.mstEquip.shortName if raw_mc.mstEquip.shortName else "",
        originalName=raw_mc.mstEquip.name,
        detail=raw_mc.mstEquip.detail,
        maxLv=raw_mc.mstEquip.maxLv,
        extraAssets=ExtraMCAssets.parse_obj(
            {
                asset_category: {
                    "male": AssetURL.mc[asset_category].format(
                        **base_settings, item_id=raw_mc.mstEquip.maleImageId
                    ),
                    "female": AssetURL.mc[asset_category].format(
                        **base_settings, item_id=raw_mc.mstEquip.femaleImageId
                    ),
                }
                for asset_category in ("item", "masterFace", "masterFigure")
            }
        ),
        expRequired=(
            [
                exp.exp
                for exp in sorted(raw_mc.mstEquipExp, key=lambda x: x.lv)
                if exp.exp != -1
            ]
        ),
        skills=[
            NiceSkill.parse_obj(skill)
            for skillEntity in raw_mc.mstSkill
            for skill in await get_nice_skill_with_svt(
                conn, skillEntity, mc_id, region, lang
            )
        ],
        costumes=[
            get_nice_mc_costume(
                region, raw_mc.mstEquip, equipAdd, raw_mc.mstCommonRelease
            )
            for equipAdd in raw_mc.mstEquipAdd
        ],
    )

    return nice_mc


async def get_all_nice_mcs(
    conn: AsyncConnection, region: Region, lang: Language, mstEquips: list[MstEquip]
) -> list[NiceMysticCode]:  # pragma: no cover
    return [
        await get_nice_mystic_code(conn, region, mstEquip.id, lang, mstEquip)
        for mstEquip in mstEquips
    ]
