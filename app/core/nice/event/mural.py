from ....config import Settings
from ....schemas.common import Region
from ....schemas.nice import AssetURL, NiceEventMural
from ....schemas.raw import MstEventMural
from ...utils import fmt_url


settings = Settings()


def get_nice_mural(region: Region, mural: MstEventMural) -> NiceEventMural:
    return NiceEventMural(
        id=mural.id,
        message=mural.message,
        imageIds=[
            fmt_url(
                AssetURL.event,
                base_url=settings.asset_url,
                region=region,
                event=f"{imageId}",
            )
            for imageId in mural.imageIds
        ],
        num=mural.num,
        condQuestId=mural.condQuestId,
        condQuestPhase=mural.condQuestPhase,
    )
