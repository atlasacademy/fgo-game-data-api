from typing import Optional

from pydantic import HttpUrl
from sqlalchemy.ext.asyncio import AsyncConnection

from ...config import Settings
from ...schemas.common import Language, Region
from ...schemas.nice import (
    AssetURL,
    ExtraAssetsUrl,
    ExtraCCAssets,
    NiceCommandCode,
    NiceSkill,
)
from ...schemas.raw import MstCommandCode
from .. import raw
from ..utils import fmt_url, get_translation
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

    base_settings: dict[str, str | int | HttpUrl] = {
        "base_url": settings.asset_url,
        "region": region,
        "item_id": cc_id,
    }
    nice_cc = NiceCommandCode(
        id=raw_cc.mstCommandCode.id,
        name=get_translation(lang, raw_cc.mstCommandCode.name),
        originalName=raw_cc.mstCommandCode.name,
        ruby=raw_cc.mstCommandCode.ruby,
        collectionNo=raw_cc.mstCommandCode.collectionNo,
        rarity=raw_cc.mstCommandCode.rarity,
        extraAssets=ExtraCCAssets(
            charaGraph=ExtraAssetsUrl(
                cc={cc_id: fmt_url(AssetURL.commandGraph, **base_settings)}
            ),
            faces=ExtraAssetsUrl(
                cc={cc_id: fmt_url(AssetURL.commandCode, **base_settings)}
            ),
        ),
        skills=[
            NiceSkill.parse_obj(skill)
            for skillEntity in raw_cc.mstSkill
            for skill in await get_nice_skill_with_svt(
                conn, skillEntity, cc_id, region, lang
            )
        ],
        illustrator=get_translation(
            lang, raw_cc.mstIllustrator.name if raw_cc.mstIllustrator else ""
        ),
        comment=(
            raw_cc.mstCommandCodeComment.comment if raw_cc.mstCommandCodeComment else ""
        ),
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
