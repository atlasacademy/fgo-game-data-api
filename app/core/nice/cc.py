from sqlalchemy.engine import Connection

from ...config import Settings
from ...data.custom_mappings import TRANSLATIONS
from ...schemas.common import Language, Region
from ...schemas.nice import AssetURL, NiceCommandCode
from .. import raw
from ..utils import get_safe
from .skill import get_nice_skill_with_svt


settings = Settings()


def get_nice_command_code(
    conn: Connection, region: Region, cc_id: int, lang: Language
) -> NiceCommandCode:
    raw_cc = raw.get_command_code_entity(conn, cc_id, expand=True)

    base_settings = {"base_url": settings.asset_url, "region": region, "item_id": cc_id}
    nice_cc = NiceCommandCode(
        id=raw_cc.mstCommandCode.id,
        name=get_safe(TRANSLATIONS, raw_cc.mstCommandCode.name)
        if lang == Language.en
        else raw_cc.mstCommandCode.name,
        collectionNo=raw_cc.mstCommandCode.collectionNo,
        rarity=raw_cc.mstCommandCode.rarity,
        extraAssets={
            "charaGraph": {
                "cc": {cc_id: AssetURL.commandGraph.format(**base_settings)}
            },
            "faces": {"cc": {cc_id: AssetURL.commandCode.format(**base_settings)}},
        },
        skills=(
            skill
            for skillEntity in raw_cc.mstSkill
            for skill in get_nice_skill_with_svt(skillEntity, cc_id, region, lang)
        ),
        illustrator=raw_cc.mstIllustrator.name if raw_cc.mstIllustrator else "",
        comment=raw_cc.mstCommandCodeComment.comment,
    )

    return nice_cc
