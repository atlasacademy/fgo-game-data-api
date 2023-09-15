from typing import Any

from ...config import Settings
from ...schemas.common import Language, Region
from ...schemas.gameenums import BUFF_TYPE_NAME
from ...schemas.nice import AssetURL
from ...schemas.raw import BuffEntityNoReverse
from ..basic import get_nice_buff_script
from ..utils import get_traits_list, get_translation


settings = Settings()


def get_nice_buff(
    buffEntity: BuffEntityNoReverse, region: Region, lang: Language
) -> dict[str, Any]:
    nice_buff: dict[str, Any] = {
        "id": buffEntity.mstBuff.id,
        "name": get_translation(lang, buffEntity.mstBuff.name),
        "originalName": buffEntity.mstBuff.name,
        "detail": buffEntity.mstBuff.detail,
        "type": BUFF_TYPE_NAME[buffEntity.mstBuff.type],
        "buffGroup": buffEntity.mstBuff.buffGroup,
        "vals": get_traits_list(buffEntity.mstBuff.vals),
        "tvals": get_traits_list(buffEntity.mstBuff.tvals),
        "ckSelfIndv": get_traits_list(buffEntity.mstBuff.ckSelfIndv),
        "ckOpIndv": get_traits_list(buffEntity.mstBuff.ckOpIndv),
        "maxRate": buffEntity.mstBuff.maxRate,
    }

    iconId = buffEntity.mstBuff.iconId
    if iconId != 0:
        nice_buff["icon"] = AssetURL.buffIcon.format(
            base_url=settings.asset_url, region=region, item_id=iconId
        )

    script = get_nice_buff_script(
        buffEntity.mstBuff,
        lambda buff: get_nice_buff(BuffEntityNoReverse(mstBuff=buff), region, lang),
    )

    nice_buff["script"] = script

    return nice_buff
