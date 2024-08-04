from ....core.utils import get_flags
from ....schemas.gameenums import BATTLE_POINT_FLAG_NAME
from ....schemas.nice import NiceBattlePoint, NiceBattlePointPhase
from ....schemas.raw import MstBattlePoint, MstBattlePointPhase


def get_nice_bp_phase(bp_phase: MstBattlePointPhase) -> NiceBattlePointPhase:
    return NiceBattlePointPhase(
        phase=bp_phase.phase,
        value=bp_phase.value,
        name=bp_phase.name,
        effectId=bp_phase.effectId,
    )


def get_nice_batte_point(
    bp: MstBattlePoint, bp_phases: list[MstBattlePointPhase]
) -> NiceBattlePoint:
    return NiceBattlePoint(
        id=bp.id,
        flags=get_flags(bp.flag, BATTLE_POINT_FLAG_NAME),
        phases=[
            get_nice_bp_phase(bp_phase)
            for bp_phase in bp_phases
            if bp_phase.battlePointId == bp.id
        ],
    )


def get_svt_bp(
    bps: list[MstBattlePoint], bp_phases: list[MstBattlePointPhase]
) -> list[NiceBattlePoint]:
    return [get_nice_batte_point(bp, bp_phases) for bp in bps]
