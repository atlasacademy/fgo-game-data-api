from sqlalchemy.ext.asyncio import AsyncConnection

from ....schemas.common import Language, Region
from ....schemas.gameenums import (
    COND_TYPE_NAME,
    SERVANT_OVERWRITE_TYPE_NAME,
    ServantOverwriteType,
)
from ....schemas.nice import NiceSvtOverwrite, NiceSvtOverwriteValue, NiceTd
from ....schemas.raw import MstSvtOverwrite, TdEntityNoReverse
from ..td import get_nice_td


async def get_nice_svt_overwrite(
    conn: AsyncConnection,
    region: Region,
    overwrite: MstSvtOverwrite,
    svt_id: int,
    td_entities: list[TdEntityNoReverse],
    lang: Language,
) -> NiceSvtOverwrite:
    if overwrite.type == ServantOverwriteType.TREASURE_DEVICE:
        td_entity = next(
            td
            for td in td_entities
            if td.mstTreasureDevice.id
            == overwrite.overwriteValue["overwriteTreasureDeviceId"]
        )
        overwriteValue = NiceSvtOverwriteValue(
            noblePhantasm=NiceTd.parse_obj(
                (await get_nice_td(conn, td_entity, svt_id, region, lang))[0]
            )
        )
    else:
        raise NotImplementedError("Unknown Svt Overwrite Type")

    return NiceSvtOverwrite(
        type=SERVANT_OVERWRITE_TYPE_NAME[overwrite.type],
        priority=overwrite.priority,
        condType=COND_TYPE_NAME[overwrite.condType],
        condTargetId=overwrite.condTargetId,
        condValue=overwrite.condValue,
        overwriteValue=overwriteValue,
    )
