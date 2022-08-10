from ....schemas.common import Region
from ....schemas.nice import NiceEventCooltime
from ....schemas.raw import MstCommonRelease, MstEventCooltimeReward
from ..common_release import get_nice_common_release
from ..gift import GiftData, get_nice_gifts


def get_nice_event_cooltime(
    region: Region,
    cooltime: MstEventCooltimeReward,
    gift_data: GiftData,
    common_release: MstCommonRelease,
) -> NiceEventCooltime:
    return NiceEventCooltime(
        spotId=cooltime.spotId,
        lv=cooltime.lv,
        name=cooltime.name,
        commonRelease=get_nice_common_release(common_release),
        cooltime=cooltime.cooltime,
        addEventPointRate=cooltime.addEventPointRate,
        gifts=get_nice_gifts(region, cooltime.giftId, gift_data),
        upperLimitGiftNum=cooltime.upperLimitGiftNum,
    )