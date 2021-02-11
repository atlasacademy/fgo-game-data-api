from typing import Any, Dict

from ...config import Settings
from ...schemas.common import Region
from ...schemas.enums import BUFF_TYPE_NAME
from ...schemas.nice import AssetURL
from ...schemas.raw import BuffEntityNoReverse
from ..basic import get_nice_buff_script
from ..utils import get_traits_list


settings = Settings()


def get_nice_buff(buffEntity: BuffEntityNoReverse, region: Region) -> Dict[str, Any]:
    buffInfo: Dict[str, Any] = {
        "id": buffEntity.mstBuff.id,
        "name": buffEntity.mstBuff.name,
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
        buffInfo["icon"] = AssetURL.buffIcon.format(
            base_url=settings.asset_url, region=region, item_id=iconId
        )

    buffInfo["script"] = get_nice_buff_script(region, buffEntity.mstBuff)

    return buffInfo
