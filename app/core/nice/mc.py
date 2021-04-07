from sqlalchemy.engine import Connection

from ...config import Settings
from ...data.custom_mappings import TRANSLATIONS
from ...schemas.common import Language, Region
from ...schemas.nice import AssetURL, NiceMysticCode
from .. import raw
from ..utils import get_safe
from .skill import get_nice_skill_with_svt


settings = Settings()


def get_nice_mystic_code(
    conn: Connection, region: Region, mc_id: int, lang: Language
) -> NiceMysticCode:
    raw_mc = raw.get_mystic_code_entity(conn, mc_id, expand=True)
    base_settings = {"base_url": settings.asset_url, "region": region}
    nice_mc = NiceMysticCode(
        id=raw_mc.mstEquip.id,
        name=get_safe(TRANSLATIONS, raw_mc.mstEquip.name)
        if lang == Language.en
        else raw_mc.mstEquip.name,
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
            for skill in get_nice_skill_with_svt(skillEntity, mc_id, region, lang)
        ),
    )

    return nice_mc
