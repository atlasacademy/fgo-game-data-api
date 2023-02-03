from ....config import Settings
from ....schemas.common import Region
from ....schemas.gameenums import (
    EVENT_FORTIFICATION_SVT_TYPE_NAME,
    EVENT_WORK_TYPE_NAME,
    SVT_CLASS_SUPPORT_GROUP_TYPE_NAME,
)
from ....schemas.nice import (
    NiceEventFortification,
    NiceEventFortificationDetail,
    NiceEventFortificationSvt,
)
from ....schemas.raw import (
    MstCommonRelease,
    MstEventFortification,
    MstEventFortificationDetail,
    MstEventFortificationSvt,
)
from ..common_release import get_nice_common_release
from ..gift import GiftData, get_nice_gifts


settings = Settings()


def get_nice_fortification_detail(
    detail: MstEventFortificationDetail,
    raw_releases: list[MstCommonRelease],
) -> NiceEventFortificationDetail:
    return NiceEventFortificationDetail(
        position=detail.position,
        name=detail.name,
        className=SVT_CLASS_SUPPORT_GROUP_TYPE_NAME[detail.classId],
        releaseConditions=[
            get_nice_common_release(release)
            for release in raw_releases
            if release.id == detail.commonReleaseId
        ],
    )


def get_nice_fortification_svt(
    svt: MstEventFortificationSvt,
    raw_releases: list[MstCommonRelease],
) -> NiceEventFortificationSvt:
    return NiceEventFortificationSvt(
        position=svt.position,
        type=EVENT_FORTIFICATION_SVT_TYPE_NAME[svt.type],
        svtId=svt.svtId,
        limitCount=svt.limitCount,
        lv=svt.lv,
        releaseConditions=[
            get_nice_common_release(release)
            for release in raw_releases
            if release.id == svt.commonReleaseId
        ],
    )


def get_nice_fortification(
    region: Region,
    fortification: MstEventFortification,
    details: list[MstEventFortificationDetail],
    servants: list[MstEventFortificationSvt],
    gift_data: GiftData,
    raw_releases: list[MstCommonRelease],
) -> NiceEventFortification:
    return NiceEventFortification(
        idx=fortification.idx,
        name=fortification.name,
        x=fortification.x,
        y=fortification.y,
        rewardSceneX=fortification.rewardSceneX,
        rewardSceneY=fortification.rewardSceneY,
        maxFortificationPoint=fortification.maxFortificationPoint,
        workType=EVENT_WORK_TYPE_NAME[fortification.workType],
        gifts=get_nice_gifts(region, fortification.giftId, gift_data),
        releaseConditions=[
            get_nice_common_release(release)
            for release in raw_releases
            if release.id == fortification.commonReleaseId
        ],
        details=[
            get_nice_fortification_detail(detail, raw_releases)
            for detail in details
            if detail.fortificationIdx == fortification.idx
        ],
        servants=[
            get_nice_fortification_svt(svt, raw_releases)
            for svt in servants
            if svt.fortificationIdx == fortification.idx
        ],
    )
