from typing import Optional

from sqlalchemy.ext.asyncio import AsyncConnection

from ...config import Settings
from ...schemas.common import Language, Region
from ...schemas.nice import AssetURL, NiceEnemyMaster, NiceEnemyMasterBattle
from ...schemas.raw import MstEnemyMaster, MstEnemyMasterBattle
from .. import raw
from ..utils import fmt_url


settings = Settings()


def get_nice_enemy_master_battle(
    region: Region,
    battle: MstEnemyMasterBattle,
) -> NiceEnemyMasterBattle:
    base_settings = {"base_url": settings.asset_url, "region": region}
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
    lang: Language,
    mstEnemyMasters: list[MstEnemyMaster],
) -> list[NiceEnemyMaster]:  # pragma: no cover
    return [
        await get_nice_enemy_master(conn, region, mstEnemyMaster.id, mstEnemyMaster)
        for mstEnemyMaster in mstEnemyMasters
    ]
