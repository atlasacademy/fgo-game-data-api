from sqlalchemy.ext.asyncio import AsyncConnection

from ...config import Settings
from ...schemas.common import Language, Region
from ...schemas.enums import get_class_name
from ...schemas.gameenums import COND_TYPE_NAME
from ...schemas.nice import NiceGrandGraph, NiceGrandGraphDetail
from ...schemas.raw import MstGrandGraph, MstGrandGraphDetail
from .. import raw
from ..utils import get_traits_list
from .item import get_nice_item_amount, get_nice_item_from_raw


settings = Settings()


def get_nice_grand_graph_detail(detail: MstGrandGraphDetail) -> NiceGrandGraphDetail:
    return NiceGrandGraphDetail(
        grandGraphId=detail.grandGraphId,
        baseClassId=detail.baseClassId,
        grandClassId=detail.grandClassId,
        baseClass=get_class_name(detail.baseClassId),
        grandClass=get_class_name(detail.grandClassId),
        adjustHp=detail.adjustHp,
        adjustAtk=detail.adjustAtk,
        condType=COND_TYPE_NAME[detail.condType],
        condTargetId=detail.condTargetId,
        condNum=detail.condNum,
        adjustIndividuality=get_traits_list(detail.adjustIndividuality),
    )


async def get_nice_grand_graph(
    conn: AsyncConnection, region: Region, grand_graph_id: int, lang: Language
) -> NiceGrandGraph:
    raw_grand_graph = await raw.get_grand_graph_entity(conn, grand_graph_id)

    mstGrandGraph = raw_grand_graph.mstGrandGraph

    items_map = {item.id: item for item in raw_grand_graph.mstItem}

    return NiceGrandGraph(
        id=mstGrandGraph.id,
        name=mstGrandGraph.name,
        nameShort=mstGrandGraph.nameShort,
        nameShortEnglish=mstGrandGraph.nameShortEnglish,
        classBoardBaseId=mstGrandGraph.classBoardBaseId,
        condSvtLv=mstGrandGraph.condSvtLv,
        condSkillLv=mstGrandGraph.condSkillLv,
        condType=COND_TYPE_NAME[mstGrandGraph.condType],
        condTargetId=mstGrandGraph.condTargetId,
        condNum=mstGrandGraph.condNum,
        removeItems=get_nice_item_amount(
            [
                get_nice_item_from_raw(region, items_map[itemId], lang)
                for itemId in mstGrandGraph.removeItemIds
            ],
            mstGrandGraph.removeItemNums,
        ),
        details=[
            get_nice_grand_graph_detail(detail)
            for detail in raw_grand_graph.mstGrandGraphDetail
            if detail.grandGraphId == mstGrandGraph.id
        ],
    )


async def get_all_nice_grand_graphs(
    conn: AsyncConnection,
    region: Region,
    mstGrandGraphs: list[MstGrandGraph],
    lang: Language,
) -> list[NiceGrandGraph]:  # pragma: no cover
    return [
        await get_nice_grand_graph(conn, region, mstGrandGraph.id, lang)
        for mstGrandGraph in mstGrandGraphs
    ]
