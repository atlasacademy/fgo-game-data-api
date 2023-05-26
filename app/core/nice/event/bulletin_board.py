from typing import Any

from ....config import Settings
from ....core.utils import fmt_url
from ....schemas.common import Region
from ....schemas.gameenums import COND_TYPE_NAME
from ....schemas.nice import (
    AssetURL,
    NiceEventBulletinBoard,
    NiceEventBulletinBoardRelease,
    NiceEventBulletinBoardScript,
)
from ....schemas.raw import MstEventBulletinBoard, MstEventBulletinBoardRelease


settings = Settings()


def get_nice_bulletin_board_release(
    bulletin_release: MstEventBulletinBoardRelease,
) -> NiceEventBulletinBoardRelease:
    return NiceEventBulletinBoardRelease(
        condGroup=bulletin_release.condGroup,
        condType=COND_TYPE_NAME[bulletin_release.condType],
        condTargetId=bulletin_release.condTargetId,
        condNum=bulletin_release.condNum,
    )


def get_nice_bulletin_board_script(
    region: Region, script: dict[str, Any], event_id: int
) -> NiceEventBulletinBoardScript:
    icon_id = script.get("iconId")
    if icon_id:
        icon = fmt_url(
            AssetURL.eventUi,
            base_url=settings.asset_url,
            region=region,
            event=f"Prefabs/{event_id}/face_{icon_id:0>3}",
        )
    else:
        icon = None
    return NiceEventBulletinBoardScript(
        name=script.get("name"),
        icon=icon,
    )


def get_nice_bulletin_board(
    region: Region,
    raw_bulletin: MstEventBulletinBoard,
    bulletin_releases: list[MstEventBulletinBoardRelease],
) -> NiceEventBulletinBoard:
    return NiceEventBulletinBoard(
        bulletinBoardId=raw_bulletin.id,
        message=raw_bulletin.message,
        probability=raw_bulletin.probability,
        dispOrder=raw_bulletin.dispOrder,
        releaseConditions=[
            get_nice_bulletin_board_release(release)
            for release in bulletin_releases
            if release.bulletinBoardId == raw_bulletin.id
        ],
        script=[
            get_nice_bulletin_board_script(
                region,
                script,
                raw_bulletin.eventId,
            )
            for script in raw_bulletin.script
        ]
        if raw_bulletin.script
        else [],
    )
