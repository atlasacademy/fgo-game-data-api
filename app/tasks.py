import asyncio
import json
import time
from pathlib import Path
from typing import Any, Iterable, Union

from aioredis import Redis
from git import Repo
from pydantic import DirectoryPath

from .config import SecretSettings, Settings, logger, project_root
from .core.basic import (
    get_all_basic_cc,
    get_all_basic_events,
    get_all_basic_mc,
    get_all_basic_wars,
    get_basic_equip,
    get_basic_servant,
)
from .core.nice.bgm import get_all_nice_bgm_entities
from .core.nice.cc import get_all_nice_cc
from .core.nice.item import get_nice_item_from_raw
from .core.nice.mc import get_all_nice_mc
from .core.nice.nice import get_nice_equip_model, get_nice_servant_model
from .core.utils import get_safe, sort_by_collection_no
from .data.custom_mappings import TRANSLATIONS
from .data.gamedata import masters, update_masters
from .db.engine import engines
from .db.helpers.cv import get_all_cvs
from .db.helpers.illustrator import get_all_illustrators
from .db.helpers.item import get_all_items
from .db.load import update_db
from .redis.load import load_redis_data
from .routers.utils import list_string
from .schemas.base import BaseModelORJson
from .schemas.common import Language, Region, RepoInfo
from .schemas.enums import ALL_ENUMS, TRAIT_NAME
from .schemas.nice import NiceEquip, NiceServant


settings = Settings()
secrets = SecretSettings()
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


async def generate_exports(
    redis: Redis, region_path: dict[Region, DirectoryPath]
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
                get_nice_item_from_raw(region, raw_item, Language.jp)
                for raw_item in get_all_items(conn)
            )
            all_illustrator_data = get_all_illustrators(conn)
            all_cv_data = get_all_cvs(conn)
            all_mc_data = get_all_nice_mc(conn, region, Language.jp)
            all_cc_data = get_all_nice_cc(conn, region, Language.jp)
            all_bgm_data = get_all_nice_bgm_entities(conn, region, Language.jp)
            all_basic_servant_data = sort_by_collection_no(
                [
                    await get_basic_servant(redis, region, svt_id)
                    for svt_id in masters[region].mstSvtServantCollectionNo.values()
                ]
            )
            all_basic_equip_data = sort_by_collection_no(
                [
                    await get_basic_equip(redis, region, svt_id)
                    for svt_id in masters[region].mstSvtEquipCollectionNo.values()
                ]
            )
            all_basic_mc_data = get_all_basic_mc(conn, region, Language.jp)
            all_basic_cc_data = sort_by_collection_no(
                get_all_basic_cc(conn, region, Language.jp)
            )
            all_basic_event_data = get_all_basic_events(conn, region, Language.jp)
            all_basic_war_data = get_all_basic_wars(conn, Language.jp)

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
                ("nice_bgm", all_bgm_data, dump_orjson),
                ("nice_illustrator", all_illustrator_data, dump_orjson),
                ("nice_cv", all_cv_data, dump_orjson),
            ]

            if region == Region.JP:
                all_basic_servant_en = sort_by_collection_no(
                    [
                        await get_basic_servant(redis, region, svt_id, lang=Language.en)
                        for svt_id in masters[region].mstSvtServantCollectionNo.values()
                    ]
                )
                all_basic_equip_en = sort_by_collection_no(
                    [
                        await get_basic_equip(redis, region, svt_id, Language.en)
                        for svt_id in masters[region].mstSvtEquipCollectionNo.values()
                    ]
                )
                all_basic_cc_en = sort_by_collection_no(
                    get_all_basic_cc(conn, region, Language.en)
                )
                all_cc_data_en = get_all_nice_cc(conn, region, Language.en)
                all_item_data_en = (
                    get_nice_item_from_raw(region, raw_item, Language.en)
                    for raw_item in get_all_items(conn)
                )
                all_basic_mc_en = get_all_basic_mc(conn, region, Language.en)
                all_mc_data_en = get_all_nice_mc(conn, region, Language.en)
                all_basic_event_data_en = get_all_basic_events(
                    conn, region, Language.en
                )
                all_basic_war_data_en = get_all_basic_wars(conn, Language.en)
                all_bgm_data_en = get_all_nice_bgm_entities(conn, region, Language.en)

                output_files = [
                    ("basic_servant_lang_en", all_basic_servant_en, dump_orjson),
                    ("basic_equip_lang_en", all_basic_equip_en, dump_orjson),
                    ("basic_event_lang_en", all_basic_event_data_en, dump_orjson),
                    ("basic_war_lang_en", all_basic_war_data_en, dump_orjson),
                    ("basic_command_code_lang_en", all_basic_cc_en, dump_orjson),
                    ("nice_command_code_lang_en", all_cc_data_en, dump_orjson),
                    ("nice_item_lang_en", all_item_data_en, dump_orjson),
                    ("basic_mystic_code_lang_en", all_basic_mc_en, dump_orjson),
                    ("nice_mystic_code_lang_en", all_mc_data_en, dump_orjson),
                    ("nice_bgm_lang_en", all_bgm_data_en, dump_orjson),
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
        if (gamedata / ".git").exists():
            repo = Repo(gamedata)
            latest_commit = repo.commit()
            repo_info[region] = RepoInfo(
                hash=latest_commit.hexsha[:6],
                timestamp=latest_commit.committed_date,  # pyright: reportGeneralTypeIssues=false
            )


async def clear_bloom_redis_cache(redis: Redis) -> None:  # pragma: no cover
    # If DEL doesn't work with the redis setup, consider calling bloom instead of redis.
    # https://github.com/valeriansaliou/bloom#can-cache-be-programatically-expired
    # The hash for bucket name "fgo-game-data-api" is "92b89e16"
    if settings.bloom_shard is not None:
        key_count = 0
        async for key in redis.iscan(match=f"bloom:{settings.bloom_shard}:c:*"):
            await redis.delete(key)
            key_count += 1
        logger.info(f"Cleared {key_count} bloom redis keys.")


async def load_and_export(
    redis: Redis, region_path: dict[Region, DirectoryPath]
) -> None:  # pragma: no cover
    if settings.write_postgres_data:
        update_db(region_path)
    if settings.write_redis_data:
        await load_redis_data(redis, region_path)
    update_masters(region_path)
    await generate_exports(redis, region_path)
    update_master_repo_info(region_path)
    await clear_bloom_redis_cache(redis)


async def pull_and_update(
    redis: Redis, region_path: dict[Region, DirectoryPath]
) -> None:  # pragma: no cover
    logger.info(f"Sleeping {settings.github_webhook_sleep} seconds …")
    await asyncio.sleep(settings.github_webhook_sleep)
    if settings.github_webhook_git_pull:
        for gamedata in region_path.values():
            if (gamedata / ".git").exists():
                repo = Repo(gamedata)
                for fetch_info in repo.remotes[0].pull():
                    commit_hash = fetch_info.commit.hexsha[:6]
                    logger.info(f"Updated {fetch_info.ref} to {commit_hash}")
    await load_and_export(redis, region_path)
