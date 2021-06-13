from typing import Generator, Optional

from sqlalchemy.engine import Connection

from ...config import Settings
from ...schemas.common import Language, Region
from ...schemas.nice import AssetURL, NiceMysticCode
from ...schemas.raw import MstEquip
from .. import raw
from ..utils import get_translation
from .skill import get_nice_skill_with_svt


settings = Settings()


def get_nice_mystic_code(
    conn: Connection,
    region: Region,
    mc_id: int,
    lang: Language,
    mstCc: Optional[MstEquip] = None,
) -> NiceMysticCode:
    raw_mc = raw.get_mystic_code_entity(conn, mc_id, True, mstCc)
    base_settings = {"base_url": settings.asset_url, "region": region}
    nice_mc = NiceMysticCode(
        id=raw_mc.mstEquip.id,
        name=get_translation(lang, raw_mc.mstEquip.name),
        detail=raw_mc.mstEquip.detail,
        maxLv=raw_mc.mstEquip.maxLv,
        extraAssets={
            asset_category: {
                "male": AssetURL.mc[asset_category].format(
                    **base_settings, item_id=raw_mc.mstEquip.maleImageId
                ),
                "female": AssetURL.mc[asset_category].format(
                    **base_settings, item_id=raw_mc.mstEquip.femaleImageId
                ),
            }
            for asset_category in ("item", "masterFace", "masterFigure")
        },
        expRequired=(
            exp.exp
            for exp in sorted(raw_mc.mstEquipExp, key=lambda x: x.lv)
            if exp.exp != -1
        ),
        skills=(
            skill
            for skillEntity in raw_mc.mstSkill
            for skill in get_nice_skill_with_svt(conn, skillEntity, mc_id, region, lang)
        ),
    )

    return nice_mc


def get_all_nice_mcs(
    conn: Connection, region: Region, lang: Language, mstEquips: list[MstEquip]
) -> Generator[NiceMysticCode, None, None]:  # pragma: no cover
    return (
        get_nice_mystic_code(conn, region, mstEquip.id, lang, mstEquip)
        for mstEquip in mstEquips
    )
