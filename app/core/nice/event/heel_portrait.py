from ....config import Settings
from ....core.utils import fmt_url, get_translation
from ....schemas.common import Language, Region
from ....schemas.gameenums import COND_TYPE_NAME
from ....schemas.nice import AssetURL, NiceHeelPortrait
from ....schemas.raw import MstHeelPortrait


settings = Settings()


def get_nice_heel_portrait(
    region: Region, event_id: int, heel_portrait: MstHeelPortrait, lang: Language
) -> NiceHeelPortrait:
    return NiceHeelPortrait(
        id=heel_portrait.id,
        name=get_translation(lang, heel_portrait.name),
        image=fmt_url(
            AssetURL.eventUi,
            base_url=settings.asset_url,
            region=region,
            event=f"Prefabs/{event_id}/{heel_portrait.imageId}",
        ),
        dispCondType=COND_TYPE_NAME[heel_portrait.dispCondType],
        dispCondId=heel_portrait.dispCondId,
        dispCondNum=heel_portrait.dispCondNum,
        script=heel_portrait.script,
    )
