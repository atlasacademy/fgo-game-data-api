from sqlalchemy.ext.asyncio import AsyncConnection

from ...config import Settings
from ...db.helpers import fetch
from ...schemas.common import Language, Region
from ...schemas.gameenums import (
    COND_TYPE_NAME,
    WAR_FLAG_NAME,
    WAR_OVERWRITE_TYPE_NAME,
    WAR_START_TYPE_NAME,
    WarEntityFlag,
    WarOverwriteType,
)
from ...schemas.nice import (
    AssetURL,
    NiceMap,
    NiceQuest,
    NiceSpot,
    NiceSpotRoad,
    NiceWar,
    NiceWarAdd,
)
from ...schemas.raw import (
    MstBgm,
    MstConstant,
    MstMap,
    MstSpot,
    MstSpotRoad,
    MstWar,
    MstWarAdd,
    QuestEntity,
)
from .. import raw
from ..utils import fmt_url, get_flags, get_translation
from .base_script import get_script_url
from .bgm import get_nice_bgm
from .quest import get_nice_quest


settings = Settings()


def get_nice_spot_road(
    region: Region, spot_road: MstSpotRoad, war_asset_id: int
) -> NiceSpotRoad:
    return NiceSpotRoad(
        id=spot_road.id,
        warId=spot_road.warId,
        mapId=spot_road.mapId,
        image=fmt_url(
            AssetURL.spotRoadImg,
            base_url=settings.asset_url,
            region=region,
            war_asset_id=war_asset_id,
        ),
        srcSpotId=spot_road.srcSpotId,
        dstSpotId=spot_road.dstSpotId,
        dispCondType=COND_TYPE_NAME[spot_road.dispCondType],
        dispTargetId=spot_road.dispTargetId,
        dispTargetValue=spot_road.dispTargetValue,
        dispCondType2=COND_TYPE_NAME[spot_road.dispCondType2],
        dispTargetId2=spot_road.dispTargetId2,
        dispTargetValue2=spot_road.dispTargetValue2,
        activeCondType=COND_TYPE_NAME[spot_road.activeCondType],
        activeTargetId=spot_road.activeTargetId,
        activeTargetValue=spot_road.activeTargetValue,
    )


def get_nice_map(region: Region, raw_map: MstMap, bgms: list[MstBgm]) -> NiceMap:
    base_settings = {"base_url": settings.asset_url, "region": region}

    bgm = get_nice_bgm(region, next(bgm for bgm in bgms if bgm.id == raw_map.bgmId))

    return NiceMap(
        id=raw_map.id,
        mapImage=fmt_url(AssetURL.mapImg, **base_settings, map_id=raw_map.mapImageId)
        if raw_map.mapImageId != 0
        else None,
        mapImageW=raw_map.mapImageW,
        mapImageH=raw_map.mapImageH,
        headerImage=fmt_url(
            AssetURL.banner,
            **base_settings,
            banner=f"img_title_header_{raw_map.headerImageId}",
        )
        if raw_map.headerImageId != 0
        else None,
        bgm=bgm,
    )


def get_nice_war_add(region: Region, war_add: MstWarAdd) -> NiceWarAdd:
    banner_url = (
        fmt_url(
            AssetURL.banner,
            base_url=settings.asset_url,
            region=region,
            banner=f"questboard_cap{war_add.overwriteId:>03}",
        )
        if war_add.type == WarOverwriteType.BANNER
        else None
    )

    return NiceWarAdd(
        warId=war_add.warId,
        type=WAR_OVERWRITE_TYPE_NAME[war_add.type],
        priority=war_add.priority,
        overwriteId=war_add.overwriteId,
        overwriteStr=war_add.overwriteStr,
        overwriteBanner=banner_url,
        condType=COND_TYPE_NAME[war_add.condType],
        targetId=war_add.targetId,
        value=war_add.value,
        startedAt=war_add.startedAt,
        endedAt=war_add.endedAt,
    )


async def get_nice_spot(
    conn: AsyncConnection,
    region: Region,
    mstWar: MstWar,
    raw_spot: MstSpot,
    war_asset_id: int,
    quests: list[QuestEntity],
    lang: Language,
) -> NiceSpot:
    return NiceSpot(
        id=raw_spot.id,
        joinSpotIds=raw_spot.joinSpotIds,
        mapId=raw_spot.mapId,
        name=get_translation(lang, raw_spot.name),
        image=fmt_url(
            AssetURL.spotImg,
            base_url=settings.asset_url,
            region=region,
            war_asset_id=war_asset_id,
            spot_id=raw_spot.imageId,
        )
        if raw_spot.imageId != 0
        else None,
        x=raw_spot.x,
        y=raw_spot.y,
        imageOfsX=raw_spot.imageOfsX,
        imageOfsY=raw_spot.imageOfsY,
        nameOfsX=raw_spot.nameOfsX,
        nameOfsY=raw_spot.nameOfsY,
        questOfsX=raw_spot.questOfsX,
        questOfsY=raw_spot.questOfsY,
        nextOfsX=raw_spot.nextOfsX,
        nextOfsY=raw_spot.nextOfsY,
        closedMessage=raw_spot.closedMessage,
        quests=[
            NiceQuest.parse_obj(
                await get_nice_quest(conn, region, quest, lang, mstWar, raw_spot)
            )
            for quest in quests
            if quest.mstQuest.spotId == raw_spot.id
        ],
    )


async def get_nice_war(
    conn: AsyncConnection, region: Region, war_id: int, lang: Language
) -> NiceWar:
    raw_war = await raw.get_war_entity(conn, war_id)

    base_settings = {"base_url": settings.asset_url, "region": region}
    war_asset_id = (
        raw_war.mstWar.assetId if raw_war.mstWar.assetId > 0 else raw_war.mstWar.id
    )

    if raw_war.mstEvent:
        banner_file = f"event_war_{raw_war.mstEvent.bannerId}"
    elif raw_war.mstWar.flag & WarEntityFlag.MAIN_SCENARIO != 0:
        last_war_id = await fetch.get_one(conn, MstConstant, "LAST_WAR_ID")
        if last_war_id and raw_war.mstWar.id <= last_war_id.value:
            banner_file = f"questboard_cap{raw_war.mstWar.bannerId:>03}"
        else:
            banner_file = "questboard_cap_closed"
    else:
        banner_file = f"chaldea_category_{raw_war.mstWar.bannerId}"

    bgm = get_nice_bgm(
        region, next(bgm for bgm in raw_war.mstBgm if bgm.id == raw_war.mstWar.bgmId)
    )

    return NiceWar(
        id=raw_war.mstWar.id,
        coordinates=raw_war.mstWar.coordinates,
        age=raw_war.mstWar.age,
        name=raw_war.mstWar.name,
        longName=get_translation(lang, raw_war.mstWar.longName),
        flags=get_flags(raw_war.mstWar.flag, WAR_FLAG_NAME),
        banner=fmt_url(AssetURL.banner, **base_settings, banner=banner_file)
        if raw_war.mstWar.bannerId != 0
        else None,
        headerImage=fmt_url(
            AssetURL.banner,
            **base_settings,
            banner=f"img_title_header_{raw_war.mstWar.headerImageId}",
        )
        if raw_war.mstWar.headerImageId != 0
        else None,
        priority=raw_war.mstWar.priority,
        parentWarId=raw_war.mstWar.parentWarId,
        materialParentWarId=raw_war.mstWar.materialParentWarId,
        emptyMessage=raw_war.mstWar.emptyMessage,
        bgm=bgm,
        scriptId=raw_war.mstWar.scriptId,
        script=get_script_url(region, raw_war.mstWar.scriptId),
        startType=WAR_START_TYPE_NAME[raw_war.mstWar.startType],
        targetId=raw_war.mstWar.targetId,
        eventId=raw_war.mstWar.eventId,
        eventName=get_translation(lang, raw_war.mstWar.eventName),
        lastQuestId=raw_war.mstWar.lastQuestId,
        warAdds=[get_nice_war_add(region, war_add) for war_add in raw_war.mstWarAdd],
        maps=[
            get_nice_map(region, raw_map, raw_war.mstBgm) for raw_map in raw_war.mstMap
        ],
        spots=[
            await get_nice_spot(
                conn,
                region,
                raw_war.mstWar,
                raw_spot,
                war_asset_id,
                raw_war.mstQuest,
                lang,
            )
            for raw_spot in raw_war.mstSpot
        ],
        spotRoads=[
            get_nice_spot_road(region, spot_road, war_asset_id)
            for spot_road in raw_war.mstSpotRoad
        ],
    )
