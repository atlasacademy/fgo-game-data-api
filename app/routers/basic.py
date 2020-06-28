import json
import logging
import time
from typing import Any, Dict, Iterable, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException

from ..config import Settings
from ..data import search
from ..data.basic import get_basic_svt
from ..data.common import Region
from ..data.gamedata import masters
from ..data.schemas.basic import BasicEquip, BasicServant
from ..data.schemas.nice import Language
from .deps import DetailMessage, EquipSearchQueryParams, ServantSearchQueryParams


logger = logging.getLogger()
settings = Settings()


def sort_by_collection_no(
    input_list: Iterable[Dict[str, Any]]
) -> Iterable[Dict[str, Any]]:  # pragma: no cover
    return sorted(input_list, key=lambda x: x["collectionNo"])


if settings.export_all_nice:  # pragma: no cover
    for region_ in (Region.NA, Region.JP):
        start_time = time.perf_counter()
        logger.info(f"Writing basic {region_} servant and equip data ...")
        all_servant_data = sort_by_collection_no(
            [
                get_basic_svt(region_, item_id)
                for item_id in masters[region_].mstSvtServantCollectionNo.values()
            ]
        )
        all_equip_data = sort_by_collection_no(
            [
                get_basic_svt(region_, item_id)
                for item_id in masters[region_].mstSvtEquipCollectionNo.values()
            ]
        )
        with open(f"export/{region_}/basic_servant.json", "w", encoding="utf-8") as fp:
            json.dump(all_servant_data, fp, ensure_ascii=False)
        with open(f"export/{region_}/basic_equip.json", "w", encoding="utf-8") as fp:
            json.dump(all_equip_data, fp, ensure_ascii=False)
        if region_ == Region.JP:
            all_servant_en = sort_by_collection_no(
                [
                    get_basic_svt(region_, item_id, Language.en)
                    for item_id in masters[region_].mstSvtServantCollectionNo.values()
                ]
            )
            with open(
                f"export/{region_}/basic_servant_lang_en.json", "w", encoding="utf-8"
            ) as fp:
                json.dump(all_servant_en, fp, ensure_ascii=False)
        run_time = time.perf_counter() - start_time
        logger.info(f"Finish writing basic {region_} data in {run_time:.4f} seconds.")


responses: Dict[Union[str, int], Any] = {
    400: {"model": DetailMessage, "description": "Insufficient query"},
    404: {"model": DetailMessage, "description": "Item not found"},
    500: {"model": DetailMessage, "description": "Internal server error"},
}


router = APIRouter()


nice_find_servant_extra = """
- **lang**: returns English servant names if querying JP data. Doesn't do anything if querying NA data.
"""


@router.get(
    "/{region}/servant/search",
    summary="Find and get servant data",
    description=ServantSearchQueryParams.DESCRIPTION + nice_find_servant_extra,
    response_description="Basic Servant Entities",
    response_model=List[BasicServant],
    response_model_exclude_unset=True,
    responses=responses,
)
async def find_servant(
    search_param: ServantSearchQueryParams = Depends(ServantSearchQueryParams),
    lang: Optional[Language] = None,
):
    if search_param.hasSearchParams:
        matches = search.search_servant(search_param)
        return [get_basic_svt(search_param.region, item, lang) for item in matches]
    else:
        raise HTTPException(status_code=400, detail="Insufficient query")


get_servant_description = """Get servant info from ID

If the given ID is a servants's collectionNo, the corresponding servant data is returned.
Otherwise, it will look up the actual ID field.

- **lang**: returns English servant names if querying JP data. Doesn't do anything if querying NA data.
"""
pre_processed_data_links = """

Preprocessed data:
- [NA servant](/export/NA/basic_servant.json)
- [JP servant](/export/JP/basic_servant.json)
- [JP servant with English names](/export/JP/basic_servant_lang_en.json)
"""

if settings.documentation_all_nice:
    get_servant_description += pre_processed_data_links


@router.get(
    "/{region}/servant/{item_id}",
    summary="Get servant data",
    response_description="Basic Servant Entity",
    response_model=BasicServant,
    response_model_exclude_unset=True,
    description=get_servant_description,
    responses=responses,
)
async def get_servant(region: Region, item_id: int, lang: Optional[Language] = None):
    if item_id in masters[region].mstSvtServantCollectionNo:
        item_id = masters[region].mstSvtServantCollectionNo[item_id]
    if item_id in masters[region].mstSvtServantCollectionNo.values():
        return get_basic_svt(region, item_id, lang)
    else:
        raise HTTPException(status_code=404, detail="Servant not found")


@router.get(
    "/{region}/equip/search",
    summary="Find and get CE data",
    description=EquipSearchQueryParams.DESCRIPTION,
    response_description="Basic Equip Entities",
    response_model=List[BasicEquip],
    response_model_exclude_unset=True,
    responses=responses,
)
async def find_equip(
    search_param: EquipSearchQueryParams = Depends(EquipSearchQueryParams),
):
    if search_param.hasSearchParams:
        matches = search.search_equip(search_param)
        return [get_basic_svt(search_param.region, item) for item in matches]
    else:
        raise HTTPException(status_code=400, detail="Insufficient query")


get_equip_description = """Get CE info from ID

If the given ID is a CE's collectionNo, the corresponding CE data is returned.
Otherwise, it will look up the actual ID field.
"""
pre_processed_equip_links = """

Preprocessed data:
- [NA CE](/export/NA/basic_equip.json)
- [JP CE](/export/JP/basic_equip.json)
"""

if settings.documentation_all_nice:
    get_equip_description += pre_processed_equip_links


@router.get(
    "/{region}/equip/{item_id}",
    summary="Get CE data",
    response_description="Basic CE Entity",
    response_model=BasicEquip,
    response_model_exclude_unset=True,
    description=get_equip_description,
    responses=responses,
)
async def get_equip(region: Region, item_id: int):
    if item_id in masters[region].mstSvtEquipCollectionNo:
        item_id = masters[region].mstSvtEquipCollectionNo[item_id]
    if item_id in masters[region].mstSvtEquipCollectionNo.values():
        return get_basic_svt(region, item_id)
    else:
        raise HTTPException(status_code=404, detail="Equip not found")
