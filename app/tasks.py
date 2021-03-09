import json
import time
from pathlib import Path
from typing import Any, Iterable, Union

import redis
from git import Repo
from pydantic import DirectoryPath

from .config import Settings, logger, project_root
from .core.basic import (
    get_basic_cc,
    get_basic_equip,
    get_basic_event,
    get_basic_mc,
    get_basic_servant,
    get_basic_war,
)
from .core.nice.cc import get_nice_command_code
from .core.nice.item import get_nice_item
from .core.nice.mc import get_nice_mystic_code
from .core.nice.nice import get_nice_equip_model, get_nice_servant_model
from .core.utils import get_safe, sort_by_collection_no
from .data.custom_mappings import TRANSLATIONS
from .data.gamedata import masters, update_masters
from .db.engine import engines
from .db.load import update_db
from .routers.utils import list_string
from .schemas.base import BaseModelORJson
from .schemas.common import Language, Region, RepoInfo
from .schemas.enums import ALL_ENUMS, TRAIT_NAME
from .schemas.nice import NiceEquip, NiceServant


settings = Settings()
REGION_PATHS = {Region.JP: settings.jp_gamedata, Region.NA: settings.na_gamedata}


export_path = project_root / "export"


def dump_normal(
    base_export_path: Path, file_name: str, data: Any
) -> None:  # pragma: no cover
    with open(base_export_path / f"{file_name}.json", "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False)


def dump_orjson(
    base_export_path: Path, file_name: str, data: Iterable[BaseModelORJson]
) -> None:  # pragma: no cover
    with open(base_export_path / f"{file_name}.json", "w", encoding="utf-8") as fp:
        fp.write(list_string(data))


def dump_svt(
    region: Region,
    base_export_path: Path,
    file_name: str,
    data: Iterable[Union[NiceServant, NiceEquip]],
) -> None:  # pragma: no cover
    export_with_lore = "["
    export_without_lore = "["
    export_with_lore_en = "["
    export_without_lore_en = "["

    for item in data:
        export_with_lore += item.json(exclude_unset=True, exclude_none=True)
        export_without_lore += item.json(
            exclude_unset=True, exclude_none=True, exclude={"profile"}
        )
        export_with_lore += ","
        export_without_lore += ","
        if region == Region.JP:
            item.name = get_safe(TRANSLATIONS, item.name)
            export_with_lore_en += item.json(exclude_unset=True, exclude_none=True)
            export_without_lore_en += item.json(
                exclude_unset=True, exclude_none=True, exclude={"profile"}
            )
            export_with_lore_en += ","
            export_without_lore_en += ","

    export_with_lore = export_with_lore.rstrip(",") + "]"
    export_without_lore = export_without_lore.rstrip(",") + "]"
    export_with_lore_en = export_with_lore_en.rstrip(",") + "]"
    export_without_lore_en = export_without_lore_en.rstrip(",") + "]"

    with open(base_export_path / f"{file_name}_lore.json", "w", encoding="utf-8") as fp:
        fp.write(export_with_lore)
    with open(base_export_path / f"{file_name}.json", "w", encoding="utf-8") as fp:
        fp.write(export_without_lore)

    if region == Region.JP:
        with open(
            base_export_path / f"{file_name}_lore_lang_en.json", "w", encoding="utf-8"
        ) as fp:
            fp.write(export_with_lore_en)
        with open(
            base_export_path / f"{file_name}_lang_en.json", "w", encoding="utf-8"
        ) as fp:
            fp.write(export_without_lore_en)


def generate_exports(
    region_path: dict[Region, DirectoryPath]
) -> None:  # pragma: no cover
    if settings.export_all_nice:
        for region in region_path:
            start_time = time.perf_counter()
            conn = engines[region].connect()
            logger.info(f"Exporting {region} data …")
            all_equip_data_lore = (
                get_nice_equip_model(conn, region, svt_id, Language.jp, lore=True)
                for svt_id in masters[region].mstSvtEquipCollectionNo.values()
            )
            all_servant_data_lore = (
                get_nice_servant_model(conn, region, svt_id, Language.jp, lore=True)
                for svt_id in masters[region].mstSvtServantCollectionNo.values()
            )
            all_item_data = (
                get_nice_item(region, item_id) for item_id in masters[region].mstItemId
            )
            all_mc_data = (
                get_nice_mystic_code(conn, region, mc_id, Language.jp)
                for mc_id in masters[region].mstEquipId
            )
            all_cc_data = (
                get_nice_command_code(conn, region, cc_id, Language.jp)
                for cc_id in masters[region].mstCommandCodeId
            )
            all_basic_servant_data = sort_by_collection_no(
                get_basic_servant(region, svt_id)
                for svt_id in masters[region].mstSvtServantCollectionNo.values()
            )
            all_basic_equip_data = sort_by_collection_no(
                get_basic_equip(region, svt_id)
                for svt_id in masters[region].mstSvtEquipCollectionNo.values()
            )
            all_basic_mc_data = (
                get_basic_mc(region, mc_id, Language.jp)
                for mc_id in masters[region].mstEquipId
            )
            all_basic_cc_data = (
                get_basic_cc(region, cc_id, Language.jp)
                for cc_id in masters[region].mstCommandCodeId
            )
            all_basic_event_data = (
                get_basic_event(region, event_id)
                for event_id in masters[region].mstEventId
            )
            all_basic_war_data = (
                get_basic_war(region, war_id) for war_id in masters[region].mstWarId
            )

            output_files = [
                ("basic_servant", all_basic_servant_data, dump_orjson),
                ("basic_equip", all_basic_equip_data, dump_orjson),
                ("basic_mystic_code", all_basic_mc_data, dump_orjson),
                ("basic_command_code", all_basic_cc_data, dump_orjson),
                ("basic_event", all_basic_event_data, dump_orjson),
                ("basic_war", all_basic_war_data, dump_orjson),
                ("nice_enums", ALL_ENUMS, dump_normal),
                ("nice_trait", TRAIT_NAME, dump_normal),
                ("nice_command_code", all_cc_data, dump_orjson),
                ("nice_item", all_item_data, dump_orjson),
                ("nice_mystic_code", all_mc_data, dump_orjson),
            ]

            if region == Region.JP:
                all_basic_servant_en = sort_by_collection_no(
                    get_basic_servant(region, svt_id, Language.en)
                    for svt_id in masters[region].mstSvtServantCollectionNo.values()
                )
                all_basic_equip_en = sort_by_collection_no(
                    get_basic_equip(region, svt_id, Language.en)
                    for svt_id in masters[region].mstSvtEquipCollectionNo.values()
                )
                all_basic_cc_en = sort_by_collection_no(
                    get_basic_cc(region, cc_id, Language.en)
                    for cc_id in masters[region].mstCommandCodeId
                )
                all_cc_data_en = (
                    get_nice_command_code(conn, region, cc_id, Language.en)
                    for cc_id in masters[region].mstCommandCodeId
                )
                all_basic_mc_en = (
                    get_basic_mc(region, mc_id, Language.en)
                    for mc_id in masters[region].mstEquipId
                )
                all_mc_data_en = (
                    get_nice_mystic_code(conn, region, mc_id, Language.en)
                    for mc_id in masters[region].mstEquipId
                )
                output_files = [
                    ("basic_servant_lang_en", all_basic_servant_en, dump_orjson),
                    ("basic_equip_lang_en", all_basic_equip_en, dump_orjson),
                    ("basic_command_code_lang_en", all_basic_cc_en, dump_orjson),
                    ("nice_command_code_lang_en", all_cc_data_en, dump_orjson),
                    ("basic_mystic_code_lang_en", all_basic_mc_en, dump_orjson),
                    ("nice_mystic_code_lang_en", all_mc_data_en, dump_orjson),
                ] + output_files

            base_export_path = export_path / region.value

            for file_name, data, dump in output_files:
                dump(base_export_path, file_name, data)

            dump_svt(
                region,
                base_export_path,
                "nice_servant",
                all_servant_data_lore,
            )
            dump_svt(
                region,
                base_export_path,
                "nice_equip",
                all_equip_data_lore,
            )

            conn.close()

            run_time = time.perf_counter() - start_time
            logger.info(f"Exported {region} data in {run_time:.2f}s.")


repo_info: dict[Region, RepoInfo] = {}


def update_master_repo_info(region_path: dict[Region, DirectoryPath]) -> None:
    for region, gamedata in region_path.items():
        if (gamedata.parent / ".git").exists():
            repo = Repo(gamedata.parent)
            latest_commit = repo.commit()
            repo_info[region] = RepoInfo(
                hash=latest_commit.hexsha[:6],
                timestamp=latest_commit.committed_date,  # pyright: reportGeneralTypeIssues=false
            )


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


def pull_and_update(
    region_path: dict[Region, DirectoryPath]
) -> None:  # pragma: no cover
    logger.info(f"Sleeping {settings.github_webhook_sleep} seconds …")
    time.sleep(settings.github_webhook_sleep)
    if settings.github_webhook_git_pull:
        for gamedata in region_path.values():
            if (gamedata.parent / ".git").exists():
                repo = Repo(gamedata.parent)
                for fetch_info in repo.remotes[0].pull():
                    commit_hash = fetch_info.commit.hexsha[:6]
                    logger.info(f"Updated {fetch_info.ref} to {commit_hash}")
    if settings.write_postgres_data:
        update_db(region_path)
    update_masters(region_path)
    generate_exports(region_path)
    update_master_repo_info(region_path)
    clear_bloom_redis_cache()
