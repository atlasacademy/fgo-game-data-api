from typing import Any

from sqlalchemy.ext.asyncio import AsyncConnection

from ...schemas.gameenums import BATTLE_POINT_FLAG_NAME
from ...schemas.nice import (
    BattlePointScriptMaxChange,
    NiceBattlePoint,
    NiceBattlePointPhase,
    NiceBattlePointScript,
    NiceSvtBattlePoint,
)
from ...schemas.raw import (
    BattlePointEntity,
    MstBattlePoint,
    MstBattlePointPhase,
    MstSvtBattlePoint,
)
from ..raw import get_battle_point_entity
from ..utils import get_flags, get_traits_list, get_traits_list_list


def get_nice_bp_phase(bp_phase: MstBattlePointPhase) -> NiceBattlePointPhase:
    return NiceBattlePointPhase(
        phase=bp_phase.phase,
        value=bp_phase.value,
        name=bp_phase.name,
        effectId=bp_phase.effectId,
    )


def get_nice_svt_bp(svt_bp: MstSvtBattlePoint) -> NiceSvtBattlePoint:
    return NiceSvtBattlePoint(
        svtId=svt_bp.svtId,
        individuality=get_traits_list_list(svt_bp.individuality)
        if svt_bp.individuality
        else None,
    )


def get_nice_bp_script(script: dict[str, Any] | None) -> NiceBattlePointScript:
    if not script:
        return NiceBattlePointScript()
    maxChanges: list[dict[str, Any]] | None = script.get("maxChange")
    return NiceBattlePointScript(
        maxChange=[
            BattlePointScriptMaxChange(
                individuality=get_traits_list(change["individuality"])
                if "individuality" in change
                else None,
                value=change.get("value"),
            )
            for change in maxChanges
        ]
        if maxChanges
        else None,
        maxLimit=script.get("maxLimit"),
        defaultMax=script.get("defaultMax"),
    )


def get_nice_battle_point_from_raw(
    bp: MstBattlePoint,
    bp_phases: list[MstBattlePointPhase],
    svt_bps: list[MstSvtBattlePoint],
) -> NiceBattlePoint:
    return NiceBattlePoint(
        id=bp.id,
        name=bp.name,
        flags=get_flags(bp.flag, BATTLE_POINT_FLAG_NAME),
        phases=[
            get_nice_bp_phase(bp_phase)
            for bp_phase in bp_phases
            if bp_phase.battlePointId == bp.id
        ],
        svts=[
            get_nice_svt_bp(svt_bp)
            for svt_bp in svt_bps
            if svt_bp.battlePointId == bp.id
        ],
        script=get_nice_bp_script(bp.script),
    )


async def get_nice_battle_point(
    conn: AsyncConnection, bp_id: int, bp_entity: BattlePointEntity | None = None
) -> NiceBattlePoint:
    if not bp_entity:
        bp_entity = await get_battle_point_entity(conn, bp_id)
    return get_nice_battle_point_from_raw(
        bp=bp_entity.mstBattlePoint,
        bp_phases=bp_entity.mstBattlePointPhase,
        svt_bps=bp_entity.mstSvtBattlePoint,
    )


def get_svt_bps(
    bps: list[MstBattlePoint],
    bp_phases: list[MstBattlePointPhase],
    svt_bps: list[MstSvtBattlePoint],
) -> list[NiceBattlePoint]:
    return [get_nice_battle_point_from_raw(bp, bp_phases, svt_bps) for bp in bps]


async def get_all_nice_battle_points(
    conn: AsyncConnection,
    mstBattlePoints: list[MstBattlePoint],
) -> list[NiceBattlePoint]:
    return [await get_nice_battle_point(conn, bp.id) for bp in mstBattlePoints]
