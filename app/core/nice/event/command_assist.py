from ....config import Settings
from ....schemas.common import Region
from ....schemas.gameenums import CARD_TYPE_NAME
from ....schemas.nice import AssetURL, NiceEventCommandAssist, NiceSkill
from ....schemas.raw import MstCommonRelease, MstEventCommandAssist
from ...utils import fmt_url
from ..common_release import get_nice_common_release


settings = Settings()


def get_nice_command_assist(
    region: Region,
    command_assist: MstEventCommandAssist,
    raw_releases: list[MstCommonRelease],
    skill: NiceSkill,
) -> NiceEventCommandAssist:
    return NiceEventCommandAssist(
        id=command_assist.id,
        priority=command_assist.priority,
        lv=command_assist.lv,
        name=command_assist.name,
        assistCard=CARD_TYPE_NAME[command_assist.assistCardId],
        image=fmt_url(
            AssetURL.event,
            base_url=settings.asset_url,
            region=region,
            event=f"{command_assist.imageId}",
        ),
        skill=skill,
        skillLv=command_assist.skillLv,
        releaseConditions=[
            get_nice_common_release(release)
            for release in raw_releases
            if release.id == command_assist.commonReleaseId
        ],
    )
