from typing import Optional

from sqlalchemy.ext.asyncio import AsyncConnection

from ...config import Settings
from ...schemas.common import Language, Region
from ...schemas.nice import AssetURL, NiceCommandCode
from ...schemas.raw import MstCommandCode
from .. import raw
from ..utils import get_translation
from .skill import get_nice_skill_with_svt


settings = Settings()


async def get_nice_command_code(
    conn: AsyncConnection,
    region: Region,
    cc_id: int,
    lang: Language,
    mstCc: Optional[MstCommandCode] = None,
) -> NiceCommandCode:
    raw_cc = await raw.get_command_code_entity(conn, cc_id, True, mstCc)

    base_settings = {"base_url": settings.asset_url, "region": region, "item_id": cc_id}
    nice_cc = NiceCommandCode(
        id=raw_cc.mstCommandCode.id,
        name=get_translation(lang, raw_cc.mstCommandCode.name),
        originalName=raw_cc.mstCommandCode.name,
        collectionNo=raw_cc.mstCommandCode.collectionNo,
        rarity=raw_cc.mstCommandCode.rarity,
        extraAssets={
            "charaGraph": {
                "cc": {cc_id: AssetURL.commandGraph.format(**base_settings)}
            },
            "faces": {"cc": {cc_id: AssetURL.commandCode.format(**base_settings)}},
        },
        skills=[
            skill
            for skillEntity in raw_cc.mstSkill
            for skill in await get_nice_skill_with_svt(
                conn, skillEntity, cc_id, region, lang
            )
        ],
        illustrator=get_translation(
            lang, raw_cc.mstIllustrator.name if raw_cc.mstIllustrator else ""
        ),
        comment=raw_cc.mstCommandCodeComment.comment,
    )

    return nice_cc


async def get_all_nice_ccs(
    conn: AsyncConnection,
    region: Region,
    lang: Language,
    mstCCommandCodes: list[MstCommandCode],
) -> list[NiceCommandCode]:  # pragma: no cover
    return [
        await get_nice_command_code(conn, region, mstCc.id, lang, mstCc)
        for mstCc in mstCCommandCodes
    ]
