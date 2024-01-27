from sqlalchemy.ext.asyncio import AsyncConnection

from ...db.helpers.gacha import get_all_gacha_entities
from ...schemas.common import Language
from ...schemas.gameenums import COND_TYPE_NAME, GACHA_FLAG_NAME, PAY_TYPE_NAME
from ...schemas.nice import GachaStoryAdjust, NiceGacha
from ...schemas.raw import GachaEntity, MstGachaStoryAdjust
from ..raw import get_gacha_entity
from ..utils import get_flags, get_translation


def get_nice_gacha_story_adjust(gacha_story: MstGachaStoryAdjust) -> GachaStoryAdjust:
    return GachaStoryAdjust(
        idx=gacha_story.idx,
        adjustId=gacha_story.adjustId,
        condType=COND_TYPE_NAME[gacha_story.condType],
        targetId=gacha_story.targetId,
        value=gacha_story.value,
        imageId=gacha_story.imageId,
    )


def get_nice_gacha(gacha: GachaEntity, lang: Language = Language.jp) -> NiceGacha:
    return NiceGacha(
        id=gacha.mstGacha.id,
        name=get_translation(lang, gacha.mstGacha.name),
        imageId=gacha.mstGacha.imageId,
        type=PAY_TYPE_NAME[gacha.mstGacha.type],
        adjustId=gacha.mstGacha.adjustId,
        pickupId=gacha.mstGacha.pickupId,
        drawNum1=gacha.mstGacha.drawNum1,
        drawNum2=gacha.mstGacha.drawNum2,
        maxDrawNum=gacha.mstGacha.maxDrawNum,
        openedAt=gacha.mstGacha.openedAt,
        closedAt=gacha.mstGacha.closedAt,
        detailUrl=gacha.mstGacha.detailUrl,
        flags=get_flags(gacha.mstGacha.flag, GACHA_FLAG_NAME),
        storyAdjusts=[
            get_nice_gacha_story_adjust(story) for story in gacha.mstGachaStoryAdjust
        ],
    )


async def get_nice_gacha_from_id(
    conn: AsyncConnection, gacha_id: int, lang: Language = Language.jp
) -> NiceGacha:
    raw_gacha = await get_gacha_entity(conn, gacha_id)
    return get_nice_gacha(raw_gacha, lang)


async def get_all_nice_gachas(
    conn: AsyncConnection, lang: Language = Language.jp
) -> list[NiceGacha]:
    all_raw = await get_all_gacha_entities(conn)
    return [get_nice_gacha(gacha, lang) for gacha in all_raw]
