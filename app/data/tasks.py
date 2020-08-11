import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Union

from git import Repo

from ..config import Settings, logger
from ..routers.utils import list_string
from .basic import get_basic_cc, get_basic_mc, get_basic_svt
from .common import Language, Region
from .enums import TRAIT_NAME
from .gamedata import masters, region_path, update_gamedata
from .nice import (
    get_nice_buff_alone,
    get_nice_command_code,
    get_nice_equip_model,
    get_nice_func_alone,
    get_nice_item,
    get_nice_mystic_code,
    get_nice_servant,
    get_nice_servant_model,
    get_nice_skill_alone,
    get_nice_td_alone,
)
from .schemas.base import BaseModelORJson


settings = Settings()


file_path = Path(__file__).resolve()
export_path = file_path.parents[2] / "export"


def dump_normal(region: Region, file_name: str, data: Any) -> None:  # pragma: no cover
    file_name = file_name + ".json"
    with open(export_path / region.value / file_name, "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False)


def dump_orjson(
    region: Region, file_name: str, data: Iterable[BaseModelORJson]
) -> None:  # pragma: no cover
    file_name = file_name + ".json"
    with open(export_path / region.value / file_name, "w", encoding="utf-8") as fp:
        fp.write(list_string(data))


def dump(region: Region, file_name: str, data: Any) -> None:  # pragma: no cover
    if isinstance(data, list) and isinstance(data[0], BaseModelORJson):
        dump_orjson(region, file_name, data)
    else:
        dump_normal(region, file_name, data)


def sort_by_collection_no(input_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(input_list, key=lambda x: x["collectionNo"])


def generate_exports() -> None:  # pragma: no cover
    if settings.export_all_nice:
        for region in region_path:
            start_time = time.perf_counter()
            logger.info(f"Exporting {region} data …")
            all_equip_data = [
                get_nice_equip_model(region, item_id, Language.jp)
                for item_id in masters[region].mstSvtEquipCollectionNo.values()
            ]
            all_servant_data = [
                get_nice_servant_model(region, item_id, Language.jp)
                for item_id in masters[region].mstSvtServantCollectionNo.values()
            ]
            all_item_data = [
                get_nice_item(region, item_id) for item_id in masters[region].mstItemId
            ]
            all_mc_data = [
                get_nice_mystic_code(region, item_id)
                for item_id in masters[region].mstEquipId
            ]
            all_cc_data = [
                get_nice_command_code(region, item_id)
                for item_id in masters[region].mstCommandCodeId
            ]
            all_basic_servant_data = sort_by_collection_no(
                [
                    get_basic_svt(region, item_id)
                    for item_id in masters[region].mstSvtServantCollectionNo.values()
                ]
            )
            all_basic_equip_data = sort_by_collection_no(
                [
                    get_basic_svt(region, item_id)
                    for item_id in masters[region].mstSvtEquipCollectionNo.values()
                ]
            )
            all_basic_mc_data = [
                get_basic_mc(region, item_id) for item_id in masters[region].mstEquipId
            ]
            all_basic_cc_data = [
                get_basic_cc(region, item_id)
                for item_id in masters[region].mstCommandCodeId
            ]

            output_files = {
                "nice_trait": TRAIT_NAME,
                "nice_command_code": all_cc_data,
                "nice_item": all_item_data,
                "nice_servant": all_servant_data,
                "nice_equip": all_equip_data,
                "nice_mystic_code": all_mc_data,
                "basic_servant": all_basic_servant_data,
                "basic_equip": all_basic_equip_data,
                "basic_mystic_code": all_basic_mc_data,
                "basic_command_code": all_basic_cc_data,
            }

            for file_name, data in output_files.items():
                dump(region, file_name, data)

            if region == Region.JP:
                all_basic_servant_en = sort_by_collection_no(
                    [
                        get_basic_svt(region, item_id, Language.en)
                        for item_id in masters[
                            region
                        ].mstSvtServantCollectionNo.values()
                    ]
                )

                dump_normal(region, "basic_servant_lang_en", all_basic_servant_en)

            run_time = time.perf_counter() - start_time
            logger.info(f"Finished exporting {region} data in {run_time:.4f}s.")


generate_exports()


repo_info: Dict[str, Dict[str, Union[str, int]]] = {}


def update_repo_info() -> None:
    for region, gamedata in region_path.items():
        if (gamedata.parent / ".git").exists():
            repo = Repo(gamedata.parent)
            latest_commit = repo.commit()
            repo_info[region] = {
                "hash": latest_commit.hexsha[:6],  # type: ignore
                "timestamp": latest_commit.committed_date,  # type: ignore
            }


update_repo_info()


def pull_and_update() -> None:  # pragma: no cover
    logger.info(f"Sleeping {settings.github_webhook_sleep} seconds …")
    time.sleep(settings.github_webhook_sleep)
    if settings.github_webhook_git_pull:
        for gamedata in region_path.values():
            if (gamedata.parent / ".git").exists():
                repo = Repo(gamedata.parent)
                for fetch_info in repo.remotes[0].pull():  # type: ignore
                    commit_hash = fetch_info.commit.hexsha[:6]
                    logger.info(f"Updated {fetch_info.ref} to {commit_hash}")
    update_gamedata()
    get_nice_servant.cache_clear()
    get_nice_buff_alone.cache_clear()
    get_nice_func_alone.cache_clear()
    get_nice_skill_alone.cache_clear()
    get_nice_td_alone.cache_clear()
    generate_exports()
    update_repo_info()
