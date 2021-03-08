from sqlalchemy.engine import Connection

from ...config import Settings
from ...data.gamedata import masters
from ...schemas.common import Region
from ...schemas.enums import WAR_START_TYPE_NAME, WarEntityFlag
from ...schemas.nice import AssetURL, NiceMap, NiceQuest, NiceSpot, NiceWar
from ...schemas.raw import MstMap, MstSpot
from .. import raw
from .bgm import get_nice_bgm
from .quest import get_nice_quest


settings = Settings()


def get_nice_map(region: Region, raw_map: MstMap) -> NiceMap:
    base_settings = {"base_url": settings.asset_url, "region": region}
    return NiceMap(
        id=raw_map.id,
        mapImage=AssetURL.mapImg.format(**base_settings, map_id=raw_map.mapImageId)
        if raw_map.mapImageId != 0
        else None,
        mapImageW=raw_map.mapImageW,
        mapImageH=raw_map.mapImageH,
        headerImage=AssetURL.banner.format(
            **base_settings, banner=f"img_title_header_{raw_map.headerImageId}"
        )
        if raw_map.headerImageId != 0
        else None,
        bgm=get_nice_bgm(region, raw_map.bgmId),
    )


def get_nice_spot(
    conn: Connection, region: Region, raw_spot: MstSpot, war_asset_id: int
) -> NiceSpot:
    return NiceSpot(
        id=raw_spot.id,
        joinSpotIds=raw_spot.joinSpotIds,
        mapId=raw_spot.mapId,
        name=raw_spot.name,
        image=AssetURL.spotImg.format(
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
        quests=(
            NiceQuest.parse_obj(get_nice_quest(region, quest))
            for quest in raw.get_quest_entity_by_spot_many(conn, [raw_spot.id])
        ),
    )


def get_nice_war(conn: Connection, region: Region, war_id: int) -> NiceWar:
    raw_war = raw.get_war_entity(conn, region, war_id)

    base_settings = {"base_url": settings.asset_url, "region": region}
    war_asset_id = (
        raw_war.mstWar.assetId if raw_war.mstWar.assetId > 0 else raw_war.mstWar.id
    )

    if raw_war.mstWar.eventId in masters[region].mstEventId:
        event = masters[region].mstEventId[raw_war.mstWar.eventId]
        banner_file = f"event_war_{event.bannerId}"
    elif raw_war.mstWar.flag & WarEntityFlag.MAIN_SCENARIO != 0:
        if raw_war.mstWar.id < masters[region].mstConstantId["LAST_WAR_ID"]:
            banner_file = f"questboard_cap{raw_war.mstWar.bannerId:>03}"
        else:
            banner_file = "questboard_cap_closed"
    else:
        banner_file = f"chaldea_category_{raw_war.mstWar.bannerId}"

    return NiceWar(
        id=raw_war.mstWar.id,
        coordinates=raw_war.mstWar.coordinates,
        age=raw_war.mstWar.age,
        name=raw_war.mstWar.name,
        longName=raw_war.mstWar.longName,
        banner=AssetURL.banner.format(**base_settings, banner=banner_file)
        if raw_war.mstWar.bannerId != 0
        else None,
        headerImage=AssetURL.banner.format(
            **base_settings, banner=f"img_title_header_{raw_war.mstWar.headerImageId}"
        )
        if raw_war.mstWar.headerImageId != 0
        else None,
        priority=raw_war.mstWar.priority,
        parentWarId=raw_war.mstWar.parentWarId,
        materialParentWarId=raw_war.mstWar.materialParentWarId,
        emptyMessage=raw_war.mstWar.emptyMessage,
        bgm=get_nice_bgm(region, raw_war.mstWar.bgmId),
        scriptId=raw_war.mstWar.scriptId,
        startType=WAR_START_TYPE_NAME[raw_war.mstWar.startType],
        targetId=raw_war.mstWar.targetId,
        eventId=raw_war.mstWar.eventId,
        lastQuestId=raw_war.mstWar.lastQuestId,
        maps=(get_nice_map(region, raw_map) for raw_map in raw_war.mstMap),
        spots=(
            get_nice_spot(conn, region, raw_spot, war_asset_id)
            for raw_spot in raw_war.mstSpot
        ),
    )
