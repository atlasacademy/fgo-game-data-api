from ....config import Settings
from ....schemas.common import Region
from ....schemas.enums import EVENT_POINT_ACTIVITY_OBJECT_NAME, ITEM_BG_TYPE_NAME
from ....schemas.nice import (
    AssetURL,
    NiceEventPointActivity,
    NiceEventPointBuff,
    NiceEventPointGroup,
)
from ....schemas.raw import MstEventPointActivity, MstEventPointBuff, MstEventPointGroup
from ...utils import fmt_url


settings = Settings()


def get_nice_pointActivity(
    point_activity: MstEventPointActivity,
) -> NiceEventPointActivity:
    return NiceEventPointActivity(
        groupId=point_activity.groupId,
        point=point_activity.point,
        objectType=EVENT_POINT_ACTIVITY_OBJECT_NAME[point_activity.objectType],
        objectId=point_activity.objectId,
        objectValue=point_activity.objectValue,
    )


def get_nice_pointGroup(
    region: Region, pointGroup: MstEventPointGroup
) -> NiceEventPointGroup:
    return NiceEventPointGroup(
        groupId=pointGroup.groupId,
        name=pointGroup.name,
        icon=fmt_url(
            AssetURL.items,
            base_url=settings.asset_url,
            region=region,
            item_id=pointGroup.iconId,
        ),
    )


def get_nice_pointBuff(
    region: Region, pointBuff: MstEventPointBuff
) -> NiceEventPointBuff:
    if pointBuff.lv is not None and pointBuff.lv > 0 and pointBuff.value == 0:
        icon = fmt_url(
            AssetURL.eventUi,
            base_url=settings.asset_url,
            region=region,
            event=f"Prefabs/{pointBuff.eventId}/img_LeaderIcon{pointBuff.imageId:0>2}",
        )
    else:
        icon = fmt_url(
            AssetURL.items,
            base_url=settings.asset_url,
            region=region,
            item_id=pointBuff.imageId,
        )
    return NiceEventPointBuff(
        id=pointBuff.id,
        funcIds=pointBuff.funcIds,
        groupId=pointBuff.groupId,
        eventPoint=pointBuff.eventPoint,
        name=pointBuff.name,
        detail=pointBuff.detail,
        icon=icon,
        background=ITEM_BG_TYPE_NAME[pointBuff.bgImageId],
        skillIcon=fmt_url(
            AssetURL.eventUi,
            base_url=settings.asset_url,
            region=region,
            event=f"Prefabs/{pointBuff.eventId}/bufficon_{pointBuff.skillIconId:0>2}",
        )
        if pointBuff.skillIconId
        else None,
        lv=pointBuff.lv,
        value=pointBuff.value,
    )
