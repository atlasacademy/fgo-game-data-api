from typing import Optional

import orjson
from orjson import JSONDecodeError
from sqlalchemy.ext.asyncio import AsyncConnection

from ...config import Settings
from ...schemas.common import Region
from ...schemas.enums import GENDER_TYPE_NAME
from ...schemas.nice import (
    AssetURL,
    NiceBattleMasterImage,
    NiceEnemyMaster,
    NiceEnemyMasterBattle,
)
from ...schemas.raw import (
    MstBattleMasterImage,
    MstCommonRelease,
    MstEnemyMaster,
    MstEnemyMasterBattle,
)
from .. import raw
from ..utils import fmt_url
from .common_release import get_nice_common_releases


settings = Settings()


def get_nice_enemy_master_battle(
    region: Region,
    battle: MstEnemyMasterBattle,
) -> NiceEnemyMasterBattle:
    base_settings = {"base_url": settings.asset_url, "region": region}
    try:
        script = orjson.loads(battle.script)
    except JSONDecodeError:
        script = {}
    if "cutinId" in script:
        cutin_ids = [int(cutin) for cutin in script["cutinId"].split(",")]
    else:
        cutin_ids = None
    return NiceEnemyMasterBattle(
        id=battle.id,
        face=fmt_url(AssetURL.enemyMasterFace, **base_settings, item_id=battle.faceId),
        figure=fmt_url(
            AssetURL.enemyMasterFigure, **base_settings, item_id=battle.faceId
        ),
        commandSpellIcon=fmt_url(
            AssetURL.commandSpell, **base_settings, item_id=battle.commandSpellIconId
        ),
        maxCommandSpell=battle.maxCommandSpell,
        offsetX=battle.offsetX,
        offsetY=battle.offsetY,
        cutin=(
            [
                fmt_url(AssetURL.enemyMasterFigure, **base_settings, item_id=cutin_id)
                for cutin_id in cutin_ids
            ]
            if cutin_ids
            else None
        ),
    )


async def get_nice_enemy_master(
    conn: AsyncConnection,
    region: Region,
    master_id: int,
    mstEnemyMaster: Optional[MstEnemyMaster] = None,
) -> NiceEnemyMaster:
    raw_master = await raw.get_enemy_master_entity(conn, master_id, mstEnemyMaster)
    return NiceEnemyMaster(
        id=raw_master.mstEnemyMaster.id,
        name=raw_master.mstEnemyMaster.name,
        battles=[
            get_nice_enemy_master_battle(region, battle)
            for battle in raw_master.mstEnemyMasterBattle
        ],
    )


async def get_all_nice_enemy_masters(
    conn: AsyncConnection,
    region: Region,
    mstEnemyMasters: list[MstEnemyMaster],
) -> list[NiceEnemyMaster]:  # pragma: no cover
    return [
        await get_nice_enemy_master(conn, region, mstEnemyMaster.id, mstEnemyMaster)
        for mstEnemyMaster in mstEnemyMasters
    ]


def get_nice_battle_master_image(
    region: Region,
    mstBattleMasterImage: MstBattleMasterImage,
    mstCommonRelease: list[MstCommonRelease],
) -> NiceBattleMasterImage:
    base_settings = {"base_url": settings.asset_url, "region": region}

    masterFaceImage = AssetURL.mc["masterFaceImage"]
    masterFigure = AssetURL.mc["masterFigure"]

    return NiceBattleMasterImage(
        id=mstBattleMasterImage.id,
        type=GENDER_TYPE_NAME[mstBattleMasterImage.type],
        faceIcon=fmt_url(
            masterFaceImage, **base_settings, item_id=mstBattleMasterImage.faceIconId
        ),
        skillCutin=fmt_url(
            masterFigure, **base_settings, item_id=mstBattleMasterImage.skillCutinId
        ),
        skillCutinOffsetX=mstBattleMasterImage.skillCutinOffsetX,
        skillCutinOffsetY=mstBattleMasterImage.skillCutinOffsetY,
        commandSpellCutin=fmt_url(
            masterFigure,
            **base_settings,
            item_id=mstBattleMasterImage.commandSpellCutinId,
        ),
        commandSpellCutinOffsetX=mstBattleMasterImage.commandSpellCutinOffsetX,
        commandSpellCutinOffsetY=mstBattleMasterImage.commandSpellCutinOffsetY,
        resultImage=fmt_url(
            masterFigure, **base_settings, item_id=mstBattleMasterImage.resultImageId
        ),
        releaseConditions=get_nice_common_releases(
            mstCommonRelease, mstBattleMasterImage.commonReleaseId
        ),
    )


async def get_nice_battle_master_images(
    conn: AsyncConnection, region: Region, image_id: int
) -> list[NiceBattleMasterImage]:
    raw_master = await raw.get_battle_master_image_entity(conn, image_id)
    return [
        get_nice_battle_master_image(
            region, mstBattleMasterImage, raw_master.mstCommonRelease
        )
        for mstBattleMasterImage in raw_master.mstBattleMasterImage
    ]
