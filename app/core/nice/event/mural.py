from ....config import Settings
from ....schemas.common import Region
from ....schemas.nice import AssetURL, NiceEventMural
from ....schemas.raw import MstEventMural
from ...utils import fmt_url

settings = Settings()


def get_nice_mural(
    region: Region, event_id: int, mural: MstEventMural
) -> NiceEventMural:
    # next mural event needs check again
    if event_id == 80614:
        fn_prefix = "img_pics_"
    else:
        fn_prefix = "img_pic_"
    return NiceEventMural(
        id=mural.id,
        message=mural.message,
        images=[
            fmt_url(
                AssetURL.eventUi,
                base_url=settings.asset_url,
                region=region,
                event=f"Prefabs/{event_id}/{fn_prefix}{imageId:03d}",
            )
            for imageId in mural.imageIds
        ],
        num=mural.num,
        condQuestId=mural.condQuestId,
        condQuestPhase=mural.condQuestPhase,
    )
