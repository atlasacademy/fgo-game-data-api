from ...schemas.gameenums import COND_TYPE_NAME
from ...schemas.nice import NiceCommonRelease
from ...schemas.raw import MstCommonRelease


def get_nice_common_release(release: MstCommonRelease) -> NiceCommonRelease:
    return NiceCommonRelease(
        id=release.id,
        priority=release.priority,
        condGroup=release.condGroup,
        condType=COND_TYPE_NAME[release.condType],
        condId=release.condId,
        condNum=release.condNum,
    )
