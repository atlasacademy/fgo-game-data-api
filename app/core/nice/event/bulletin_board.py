from ....schemas.gameenums import COND_TYPE_NAME
from ....schemas.nice import NiceEventBulletinBoard, NiceEventBulletinBoardRelease
from ....schemas.raw import MstEventBulletinBoard, MstEventBulletinBoardRelease


def get_nice_bulletin_board_release(
    bulletin_release: MstEventBulletinBoardRelease,
) -> NiceEventBulletinBoardRelease:
    return NiceEventBulletinBoardRelease(
        condGroup=bulletin_release.condGroup,
        condType=COND_TYPE_NAME[bulletin_release.condType],
        condTargetId=bulletin_release.condTargetId,
        condNum=bulletin_release.condNum,
    )


def get_nice_bulletin_board(
    raw_bulletin: MstEventBulletinBoard,
    bulletin_releases: list[MstEventBulletinBoardRelease],
) -> NiceEventBulletinBoard:
    return NiceEventBulletinBoard(
        bulletinBoardId=raw_bulletin.id,
        message=raw_bulletin.message,
        probability=raw_bulletin.probability,
        releaseConditions=[
            get_nice_bulletin_board_release(release)
            for release in bulletin_releases
            if release.bulletinBoardId == raw_bulletin.id
        ],
    )
