from sqlalchemy.ext.asyncio import AsyncConnection

from ...schemas.gameenums import BATTLE_SCRIPT_ACTION_TYPE_NAME
from ...schemas.nice import NiceBattleScript
from ...schemas.raw import BattleScriptEntity, MstBattleScript
from .. import raw


def get_nice_battle_script(script: MstBattleScript) -> NiceBattleScript:
    return NiceBattleScript(
        id=script.id,
        playOrder=script.playOrder,
        idx=script.idx,
        battleScriptAction=BATTLE_SCRIPT_ACTION_TYPE_NAME[script.battleScriptAction],
        script=script.script,
    )


async def get_nice_battle_scripts(
    conn: AsyncConnection,
    script_id: int,
    battle_script_entity: BattleScriptEntity | None = None,
) -> list[NiceBattleScript]:
    if not battle_script_entity:
        battle_script_entity = await raw.get_battle_script_entity(conn, script_id)
    return [
        get_nice_battle_script(script)
        for script in battle_script_entity.mstBattleScript
    ]
