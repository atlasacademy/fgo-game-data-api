from ....schemas.common import Region
from ....schemas.nice import NiceEventCooltimeReward
from ....schemas.raw import MstCommonRelease, MstEventCooltimeReward
from ..common_release import get_nice_common_release
from ..gift import GiftData, get_nice_gifts


def get_nice_event_cooltime(
    region: Region,
    cooltime: MstEventCooltimeReward,
    gift_data: GiftData,
    raw_releases: list[MstCommonRelease],
) -> NiceEventCooltimeReward:
    return NiceEventCooltimeReward(
        spotId=cooltime.spotId,
        lv=cooltime.lv,
        name=cooltime.name,
        releaseConditions=[
            get_nice_common_release(release)
            for release in raw_releases
            if release.id == cooltime.commonReleaseId
        ],
        cooltime=cooltime.cooltime,
        addEventPointRate=cooltime.addEventPointRate,
        gifts=get_nice_gifts(region, cooltime.giftId, gift_data),
        upperLimitGiftNum=cooltime.upperLimitGiftNum,
    )
