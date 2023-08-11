from ....config import Settings
from ....schemas.common import Region
from ....schemas.enums import ITEM_BG_TYPE_NAME
from ....schemas.nice import AssetURL, NiceEventPointBuff, NiceEventPointGroup
from ....schemas.raw import MstEventPointBuff, MstEventPointGroup
from ...utils import fmt_url


settings = Settings()


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
    return NiceEventPointBuff(
        id=pointBuff.id,
        funcIds=pointBuff.funcIds,
        groupId=pointBuff.groupId,
        eventPoint=pointBuff.eventPoint,
        name=pointBuff.name,
        detail=pointBuff.detail,
        icon=fmt_url(
            AssetURL.items,
            base_url=settings.asset_url,
            region=region,
            item_id=pointBuff.imageId,
        ),
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
