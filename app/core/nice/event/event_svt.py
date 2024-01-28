from typing import Any

from ....schemas.gameenums import EVENT_SVT_TYPE_NAME
from ....schemas.nice import NiceEventSvt, NiceEventSvtScript
from ....schemas.raw import MstCommonRelease, MstEventSvt
from ..common_release import get_nice_common_releases


def get_nice_event_svt_script(
    script: dict[str, Any], raw_releases: list[MstCommonRelease]
) -> NiceEventSvtScript:
    out: dict[str, Any] = {}

    for unchanged_key in (
        "addGetMessage",
        "joinQuestId",
        "joinShopId",
        "notPresentRarePri",
        "ruby",
    ):
        if unchanged_key in script:
            out[unchanged_key] = script[unchanged_key]

    for bool_key in ("isProtectedDuringEvent", "notPresentAnonymous"):
        if bool_key in script:
            out[bool_key] = script[bool_key] == 1

    if "addMessageCommonReleaseId" in script:
        out["addMessageReleaseConditions"] = get_nice_common_releases(
            raw_releases, script["addMessageCommonReleaseId"]
        )

    return NiceEventSvtScript.parse_obj(out)


def get_nice_event_svt(
    event_svt: MstEventSvt, raw_releases: list[MstCommonRelease]
) -> NiceEventSvt:
    return NiceEventSvt(
        svtId=event_svt.svtId,
        script=get_nice_event_svt_script(event_svt.script, raw_releases),
        originalScript=event_svt.script,
        type=EVENT_SVT_TYPE_NAME[event_svt.type],
        joinMessage=event_svt.joinMessage,
        getMessage=event_svt.getMessage,
        leaveMessage=event_svt.leaveMessage,
        name=event_svt.name,
        battleName=event_svt.battleName,
        releaseConditions=get_nice_common_releases(
            raw_releases, event_svt.commonReleaseId
        ),
        startedAt=event_svt.startedAt,
        endedAt=event_svt.endedAt,
    )
