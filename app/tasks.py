import json
import time
from typing import Any, Dict, Iterable

import redis
from git import Repo
from pydantic import BaseModel

from .config import Settings, logger, project_root
from .core.basic import (
    get_basic_cc,
    get_basic_equip,
    get_basic_event,
    get_basic_mc,
    get_basic_servant,
    get_basic_war,
)
from .core.nice import (
    get_nice_command_code,
    get_nice_equip_model,
    get_nice_item,
    get_nice_mystic_code,
    get_nice_servant_model,
)
from .core.utils import get_lang_en, sort_by_collection_no
from .data.gamedata import masters, region_path, update_db, update_gamedata
from .db.base import engines
from .routers.utils import list_string, list_string_exclude
from .schemas.base import BaseModelORJson
from .schemas.common import Language, Region
from .schemas.enums import ALL_ENUMS, TRAIT_NAME


settings = Settings()


export_path = project_root / "export"


def dump_normal(region: Region, file_name: str, data: Any) -> None:  # pragma: no cover
    file_name = file_name + ".json"
    with open(export_path / region.value / file_name, "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False)


def dump_orjson(
    region: Region, file_name: str, data: Iterable[BaseModelORJson]
) -> None:  # pragma: no cover
    file_name = file_name + ".json"
    if file_name in {
        "nice_servant.json",
        "nice_equip.json",
        "nice_servant_lang_en.json",
        "nice_equip_lang_en.json",
    }:
        with open(export_path / region.value / file_name, "w", encoding="utf-8") as fp:
            fp.write(list_string_exclude(data, exclude={"profile"}))
    else:
        with open(export_path / region.value / file_name, "w", encoding="utf-8") as fp:
            fp.write(list_string(data))


def dump(region: Region, file_name: str, data: Any) -> None:  # pragma: no cover
    if isinstance(data, list) and isinstance(data[0], BaseModelORJson):
        dump_orjson(region, file_name, data)
    else:
        dump_normal(region, file_name, data)


def generate_exports() -> None:  # pragma: no cover
    if settings.export_all_nice:
        for region in region_path:
            start_time = time.perf_counter()
            conn = engines[region].connect()
            logger.info(f"Exporting {region} data …")
            all_equip_data_lore = [
                get_nice_equip_model(conn, region, svt_id, Language.jp, lore=True)
                for svt_id in masters[region].mstSvtEquipCollectionNo.values()
            ]
            all_servant_data_lore = [
                get_nice_servant_model(conn, region, svt_id, Language.jp, lore=True)
                for svt_id in masters[region].mstSvtServantCollectionNo.values()
            ]
            all_item_data = [
                get_nice_item(region, item_id) for item_id in masters[region].mstItemId
            ]
            all_mc_data = [
                get_nice_mystic_code(conn, region, mc_id)
                for mc_id in masters[region].mstEquipId
            ]
            all_cc_data = [
                get_nice_command_code(conn, region, cc_id)
                for cc_id in masters[region].mstCommandCodeId
            ]
            all_basic_servant_data = sort_by_collection_no(
                get_basic_servant(region, svt_id)
                for svt_id in masters[region].mstSvtServantCollectionNo.values()
            )
            all_basic_equip_data = sort_by_collection_no(
                get_basic_equip(region, svt_id)
                for svt_id in masters[region].mstSvtEquipCollectionNo.values()
            )
            all_basic_mc_data = [
                get_basic_mc(region, mc_id) for mc_id in masters[region].mstEquipId
            ]
            all_basic_cc_data = [
                get_basic_cc(region, cc_id)
                for cc_id in masters[region].mstCommandCodeId
            ]
            all_basic_event_data = [
                get_basic_event(region, event_id)
                for event_id in masters[region].mstEventId
            ]
            all_basic_war_data = [
                get_basic_war(region, war_id) for war_id in masters[region].mstWarId
            ]

            output_files = {
                "nice_enums": ALL_ENUMS,
                "nice_trait": TRAIT_NAME,
                "nice_command_code": all_cc_data,
                "nice_item": all_item_data,
                "nice_servant": all_servant_data_lore,
                "nice_servant_lore": all_servant_data_lore,
                "nice_equip": all_equip_data_lore,
                "nice_equip_lore": all_equip_data_lore,
                "nice_mystic_code": all_mc_data,
                "basic_servant": all_basic_servant_data,
                "basic_equip": all_basic_equip_data,
                "basic_mystic_code": all_basic_mc_data,
                "basic_command_code": all_basic_cc_data,
                "basic_event": all_basic_event_data,
                "basic_war": all_basic_war_data,
            }

            if region == Region.JP:
                all_basic_servant_en = sort_by_collection_no(
                    get_basic_servant(region, svt_id, Language.en)
                    for svt_id in masters[region].mstSvtServantCollectionNo.values()
                )
                all_basic_equip_en = sort_by_collection_no(
                    get_basic_equip(region, svt_id, Language.en)
                    for svt_id in masters[region].mstSvtEquipCollectionNo.values()
                )
                all_nice_servant_en = [
                    get_lang_en(svt) for svt in all_servant_data_lore
                ]
                all_nice_equip_en = [get_lang_en(svt) for svt in all_equip_data_lore]
                output_files.update(
                    {
                        "nice_servant_lang_en": all_nice_servant_en,
                        "nice_servant_lore_lang_en": all_nice_servant_en,
                        "nice_equip_lang_en": all_nice_equip_en,
                        "nice_equip_lore_lang_en": all_nice_equip_en,
                        "basic_servant_lang_en": all_basic_servant_en,
                        "basic_equip_lang_en": all_basic_equip_en,
                    }
                )

            for file_name, data in output_files.items():
                dump(region, file_name, data)

            conn.close()

            run_time = time.perf_counter() - start_time
            logger.info(f"Exported {region} data in {run_time:.2f}s.")


generate_exports()


class RepoInfo(BaseModel):
    hash: str
    timestamp: int


repo_info: Dict[Region, RepoInfo] = {}


def update_repo_info() -> None:
    for region, gamedata in region_path.items():
        if (gamedata.parent / ".git").exists():
            repo = Repo(gamedata.parent)
            latest_commit = repo.commit()
            repo_info[region] = RepoInfo(
                hash=latest_commit.hexsha[:6],
                timestamp=latest_commit.committed_date,  # pyright: reportGeneralTypeIssues=false
            )


update_repo_info()


def clear_bloom_redis_cache() -> None:  # pragma: no cover
    # If DEL doesn't work with the redis setup, consider calling bloom instead of redis.
    # https://github.com/valeriansaliou/bloom#can-cache-be-programatically-expired
    # The hash for bucket name "fgo-game-data-api" is "92b89e16"
    if settings.redis_host:
        redis_server = redis.Redis(
            settings.redis_host, port=settings.redis_port, db=settings.redis_db
        )
        key_count = 0
        for key in redis_server.scan_iter(f"bloom:{settings.bloom_shard}:c:*"):
            redis_server.delete(key)
            key_count += 1
        logger.info(f"Cleared {key_count} redis keys.")


clear_bloom_redis_cache()


def pull_and_update() -> None:  # pragma: no cover
    logger.info(f"Sleeping {settings.github_webhook_sleep} seconds …")
    time.sleep(settings.github_webhook_sleep)
    if settings.github_webhook_git_pull:
        for gamedata in region_path.values():
            if (gamedata.parent / ".git").exists():
                repo = Repo(gamedata.parent)
                for fetch_info in repo.remotes[0].pull():
                    commit_hash = fetch_info.commit.hexsha[:6]
                    logger.info(f"Updated {fetch_info.ref} to {commit_hash}")
    update_gamedata()
    if settings.write_postgres_data:
        update_db()
    generate_exports()
    update_repo_info()
    clear_bloom_redis_cache()
