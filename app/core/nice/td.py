from copy import deepcopy
from typing import Any, Dict, List

from ...config import Settings
from ...schemas.common import Region
from ...schemas.enums import CARD_TYPE_NAME
from ...schemas.nice import AssetURL
from ...schemas.raw import TdEntityNoReverse
from ..utils import get_traits_list, strip_formatting_brackets
from .func import get_nice_base_function, parse_dataVals


settings = Settings()


def get_nice_td(
    tdEntity: TdEntityNoReverse, svtId: int, region: Region
) -> List[Dict[str, Any]]:
    nice_td: Dict[str, Any] = {
        "id": tdEntity.mstTreasureDevice.id,
        "name": tdEntity.mstTreasureDevice.name,
        "ruby": tdEntity.mstTreasureDevice.ruby,
        "rank": tdEntity.mstTreasureDevice.rank,
        "type": tdEntity.mstTreasureDevice.typeText,
        "individuality": get_traits_list(tdEntity.mstTreasureDevice.individuality),
    }

    if tdEntity.mstTreasureDeviceDetail:
        nice_td["detail"] = strip_formatting_brackets(
            tdEntity.mstTreasureDeviceDetail[0].detail
        )

    nice_td["npGain"] = {
        "buster": [td_lv.tdPointB for td_lv in tdEntity.mstTreasureDeviceLv],
        "arts": [td_lv.tdPointA for td_lv in tdEntity.mstTreasureDeviceLv],
        "quick": [td_lv.tdPointQ for td_lv in tdEntity.mstTreasureDeviceLv],
        "extra": [td_lv.tdPointEx for td_lv in tdEntity.mstTreasureDeviceLv],
        "np": [td_lv.tdPoint for td_lv in tdEntity.mstTreasureDeviceLv],
        "defence": [td_lv.tdPointDef for td_lv in tdEntity.mstTreasureDeviceLv],
    }

    nice_td["functions"] = []

    for funci, _ in enumerate(tdEntity.mstTreasureDeviceLv[0].funcId):
        function = tdEntity.mstTreasureDeviceLv[0].expandedFuncId[funci]
        functionInfo = get_nice_base_function(function, region)
        for sval in ["svals", "svals2", "svals3", "svals4", "svals5"]:
            functionInfo[sval] = [
                parse_dataVals(
                    getattr(mst_td, sval)[funci], function.mstFunc.funcType, region
                )
                for mst_td in tdEntity.mstTreasureDeviceLv
            ]
        nice_td["functions"].append(functionInfo)

    chosen_svts = [
        svt_td for svt_td in tdEntity.mstSvtTreasureDevice if svt_td.svtId == svtId
    ]
    out_tds = []
    for chosen_svt in chosen_svts:
        out_td = deepcopy(nice_td)
        imageId = chosen_svt.imageIndex
        base_settings_id = {
            "base_url": settings.asset_url,
            "region": region,
            "item_id": svtId,
        }
        if imageId < 2:
            file_i = "np"
        else:
            file_i = "np" + str(imageId // 2)
        out_td.update(
            {
                "icon": AssetURL.commands.format(**base_settings_id, i=file_i),
                "strengthStatus": chosen_svt.strengthStatus,
                "num": chosen_svt.num,
                "priority": chosen_svt.priority,
                "condQuestId": chosen_svt.condQuestId,
                "condQuestPhase": chosen_svt.condQuestPhase,
                "card": CARD_TYPE_NAME[chosen_svt.cardId],
                "npDistribution": chosen_svt.damage,
            }
        )
        out_tds.append(out_td)
    return out_tds
