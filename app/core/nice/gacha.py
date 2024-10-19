from sqlalchemy.ext.asyncio import AsyncConnection

from ...schemas.common import Language
from ...schemas.gameenums import COND_TYPE_NAME, GACHA_FLAG_NAME, PAY_TYPE_NAME
from ...schemas.nice import GachaStoryAdjust, NiceGacha, NiceGachaSub
from ...schemas.raw import (
    GachaEntity,
    MstCommonRelease,
    MstGachaStoryAdjust,
    MstGachaSub,
)
from ..raw import get_gacha_entity
from ..utils import get_flags, get_translation
from .common_release import get_nice_common_release


def get_nice_gacha_story_adjust(gacha_story: MstGachaStoryAdjust) -> GachaStoryAdjust:
    return GachaStoryAdjust(
        idx=gacha_story.idx,
        adjustId=gacha_story.adjustId,
        condType=COND_TYPE_NAME[gacha_story.condType],
        targetId=gacha_story.targetId,
        value=gacha_story.value,
        imageId=gacha_story.imageId,
    )


def get_nice_gacha_sub(
    gacha_sub: MstGachaSub,
    raw_releases: list[MstCommonRelease],
) -> NiceGachaSub:
    return NiceGachaSub(
        id=gacha_sub.id,
        priority=gacha_sub.priority,
        imageId=gacha_sub.imageId,
        adjustAddId=gacha_sub.adjustAddId,
        openedAt=gacha_sub.openedAt,
        closedAt=gacha_sub.closedAt,
        releaseConditions=[
            get_nice_common_release(release)
            for release in raw_releases
            if release.id == gacha_sub.commonReleaseId
        ],
        script=gacha_sub.script,
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
        gachaSubs=[
            get_nice_gacha_sub(gacha_sub, gacha.mstCommonRelease)
            for gacha_sub in gacha.mstGachaSub
        ],
        featuredSvtIds=(
            gacha.viewGachaFeaturedSvt[0].svtIds if gacha.viewGachaFeaturedSvt else []
        ),
    )


async def get_nice_gacha_from_id(
    conn: AsyncConnection, gacha_id: int, lang: Language = Language.jp
) -> NiceGacha:
    raw_gacha = await get_gacha_entity(conn, gacha_id)
    return get_nice_gacha(raw_gacha, lang)


def get_all_nice_gachas(
    gachas: list[GachaEntity], lang: Language = Language.jp
) -> list[NiceGacha]:
    return [get_nice_gacha(gacha, lang) for gacha in gachas]
