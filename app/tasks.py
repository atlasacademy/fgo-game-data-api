import asyncio
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Union

import aiofiles
import httpx
import orjson
import psutil
from fastapi.concurrency import run_in_threadpool
from git import Repo
from pydantic import DirectoryPath
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from .config import EXTRA_SVT_ID_IN_NICE, Settings, get_app_info, logger, project_root
from .core.basic import (
    get_all_basic_ccs,
    get_all_basic_equips,
    get_all_basic_events,
    get_all_basic_mcs,
    get_all_basic_servants,
    get_all_basic_wars,
)
from .core.nice.bgm import get_all_nice_bgms
from .core.nice.cc import get_all_nice_ccs
from .core.nice.class_board import get_all_nice_class_boards
from .core.nice.enemy_master import get_all_nice_enemy_masters
from .core.nice.event.event import get_nice_event
from .core.nice.event.shop import get_nice_shops_from_raw
from .core.nice.gacha import get_all_nice_gachas
from .core.nice.grand_graph import get_all_nice_grand_graphs
from .core.nice.item import get_all_nice_items
from .core.nice.mc import get_all_nice_mcs
from .core.nice.mm import get_all_nice_mms
from .core.nice.nice import get_nice_equip_model, get_nice_servant_model
from .core.nice.war import get_nice_war
from .core.raw import get_all_bgm_entities, get_servant_entity
from .core.utils import get_translation
from .data.extra import get_extra_svt_data
from .db.engine import engines
from .db.helpers import fetch
from .db.helpers.gacha import get_all_gacha_entities
from .db.load import load_pydantic_to_db, update_db
from .export.constants import export_constants
from .models.raw import mstSvtExtra
from .redis import Redis
from .redis.helpers.repo_version import (
    get_region_version,
    get_repo_version,
    set_region_version,
    set_repo_version,
)
from .redis.load import load_redis_data, load_svt_extra_redis
from .routers.utils import list_string
from .schemas.base import BaseModelORJson
from .schemas.common import Language, Region, RegionInfo, RepoInfo
from .schemas.enums import ALL_ENUMS, TRAIT_NAME
from .schemas.gameenums import NiceItemType, SvtType
from .schemas.nice import (
    NiceEquip,
    NiceEvent,
    NiceGacha,
    NiceItem,
    NiceMasterMission,
    NiceServant,
    NiceShop,
)
from .schemas.raw import (
    AssetStorageLine,
    BgmEntity,
    GachaEntity,
    MstClassBoardBase,
    MstCommandCode,
    MstConstant,
    MstCv,
    MstEnemyMaster,
    MstEquip,
    MstEvent,
    MstGrandGraph,
    MstIllustrator,
    MstItem,
    MstMasterMission,
    MstShop,
    MstSvt,
    MstWar,
    ServantEntity,
)

settings = Settings()


async def dump_normal(
    export_path: Path, file_name: str, data: Any
) -> None:  # pragma: no cover
    async with aiofiles.open(export_path / f"{file_name}.json", "wb") as fp:
        await fp.write(orjson.dumps(data, option=orjson.OPT_NON_STR_KEYS))


async def dump_orjson(
    export_path: Path, file_name: str, data: Iterable[BaseModelORJson]
) -> None:  # pragma: no cover
    async with aiofiles.open(
        export_path / f"{file_name}.json", "w", encoding="utf-8"
    ) as fp:
        await fp.write(list_string(data))


@dataclass
class ExportUtil:
    redis: Redis
    region: Region
    export_path: Path
    lang: Language = Language.jp

    def append_file_name(self, file_name: str) -> str:  # pragma: no cover
        if self.lang == Language.en:
            return file_name + "_lang_en"
        return file_name

    async def dump_orjson(
        self, file_name: str, data: Iterable[BaseModelORJson]
    ) -> None:  # pragma: no cover
        await dump_orjson(self.export_path, self.append_file_name(file_name), data)

    async def dump_orjson_object(
        self, file_name: str, data: BaseModelORJson
    ) -> None:  # pragma: no cover
        async with aiofiles.open(
            self.export_path / f"{self.append_file_name(file_name)}.json",
            "w",
            encoding="utf-8",
        ) as fp:
            await fp.write(data.json())


async def get_nice_svt(
    conn: AsyncConnection,
    region: Region,
    lang: Language,
    lore: bool,
    raw_svt: ServantEntity,
) -> Union[NiceServant, NiceEquip]:  # pragma: no cover
    if raw_svt.mstSvt.type == SvtType.SERVANT_EQUIP:
        return await get_nice_equip_model(
            conn=conn,
            region=region,
            item_id=raw_svt.mstSvt.id,
            lang=lang,
            lore=True,
            raw_svt=raw_svt,
        )
    else:
        return await get_nice_servant_model(
            conn=conn,
            region=region,
            item_id=raw_svt.mstSvt.id,
            lang=lang,
            lore=lore,
            raw_svt=raw_svt,
        )


async def dump_svt(
    conn: AsyncConnection, util: ExportUtil, file_name: str, svts: list[MstSvt]
) -> None:  # pragma: no cover
    region = util.region
    export_path = util.export_path

    with_lore: list[str] = []
    without_lore: list[str] = []
    with_lore_en: list[str] = []
    without_lore_en: list[str] = []

    for svt in svts:
        raw_svt = await get_servant_entity(
            conn, svt.id, expand=True, lore=True, mstSvt=svt
        )

        nice_svt = await get_nice_svt(conn, region, Language.jp, True, raw_svt)
        with_lore.append(nice_svt.json(exclude_unset=True, exclude_none=True))
        without_lore.append(
            nice_svt.json(exclude={"profile"}, exclude_unset=True, exclude_none=True)
        )

        if region == Region.JP:
            nice_svt_en = await get_nice_svt(conn, region, Language.en, True, raw_svt)
            with_lore_en.append(nice_svt_en.json(exclude_unset=True, exclude_none=True))
            without_lore_en.append(
                nice_svt_en.json(
                    exclude={"profile"}, exclude_unset=True, exclude_none=True
                )
            )

    out_name = export_path / f"{file_name}.json"
    out_lore_name = export_path / f"{file_name}_lore.json"

    async with aiofiles.open(out_lore_name, "w", encoding="utf-8") as fp:
        await fp.write("[" + ",".join(with_lore) + "]")
    async with aiofiles.open(out_name, "w", encoding="utf-8") as fp:
        await fp.write("[" + ",".join(without_lore) + "]")

    if region == Region.JP:
        out_name_en = export_path / f"{file_name}_lang_en.json"
        out_lore_name_en = export_path / f"{file_name}_lore_lang_en.json"

        async with aiofiles.open(out_lore_name_en, "w", encoding="utf-8") as fp:
            await fp.write("[" + ",".join(with_lore_en) + "]")
        async with aiofiles.open(out_name_en, "w", encoding="utf-8") as fp:
            await fp.write("[" + ",".join(without_lore_en) + "]")


def get_nice_items_from_raw(
    util: ExportUtil, items: list[MstItem]
) -> list[NiceItem]:  # pragma: no cover
    return get_all_nice_items(util.region, util.lang, items)


async def dump_nice_items(
    util: ExportUtil, all_item_data: list[NiceItem]
) -> None:  # pragma: no cover
    await util.dump_orjson("nice_item", all_item_data)


async def dump_nice_ccs(
    conn: AsyncConnection, util: ExportUtil, ccs: list[MstCommandCode]
) -> None:  # pragma: no cover
    all_cc_data = await get_all_nice_ccs(conn, util.region, util.lang, ccs)
    await util.dump_orjson("nice_command_code", all_cc_data)


async def dump_nice_mcs(
    conn: AsyncConnection, util: ExportUtil, mcs: list[MstEquip]
) -> None:  # pragma: no cover
    all_mc_data = await get_all_nice_mcs(conn, util.region, util.lang, mcs)
    await util.dump_orjson("nice_mystic_code", all_mc_data)


async def dump_nice_enemy_masters(
    conn: AsyncConnection, util: ExportUtil, mcs: list[MstEnemyMaster]
) -> None:  # pragma: no cover
    all_enemy_master_data = await get_all_nice_enemy_masters(conn, util.region, mcs)
    await util.dump_orjson("nice_enemy_master", all_enemy_master_data)


async def dump_nice_class_boards(
    conn: AsyncConnection, util: ExportUtil, boards: list[MstClassBoardBase]
) -> None:  # pragma: no cover
    all_class_board_data = await get_all_nice_class_boards(
        conn, util.region, boards, util.lang
    )
    await util.dump_orjson("nice_class_board", all_class_board_data)


async def dump_nice_grand_graphs(
    conn: AsyncConnection, util: ExportUtil, graphs: list[MstGrandGraph]
) -> None:  # pragma: no cover
    all_grand_graph_data = await get_all_nice_grand_graphs(
        conn, util.region, graphs, util.lang
    )
    await util.dump_orjson("nice_grand_graph", all_grand_graph_data)


async def dump_nice_bgms(
    util: ExportUtil, bgms: list[BgmEntity]
) -> None:  # pragma: no cover
    all_bgm_data = get_all_nice_bgms(util.region, util.lang, bgms)
    await util.dump_orjson("nice_bgm", all_bgm_data)


async def dump_nice_gachas(util: ExportUtil, gachas: list[GachaEntity]) -> None:
    await util.dump_orjson("nice_gacha", get_all_nice_gachas(gachas, util.lang))


async def get_nice_mms_from_raw(
    conn: AsyncConnection, util: ExportUtil, mms: list[MstMasterMission]
) -> list[NiceMasterMission]:  # pragma: no cover
    return await get_all_nice_mms(conn, util.region, mms, util.lang)


async def dump_nice_mms(
    util: ExportUtil, all_mm_data: list[NiceMasterMission]
) -> None:  # pragma: no cover
    await util.dump_orjson("nice_master_mission", all_mm_data)


async def dump_nice_wars(
    conn: AsyncConnection, util: ExportUtil, wars: list[MstWar]
) -> None:  # pragma: no cover
    all_war_data = [
        await get_nice_war(conn, util.region, war.id, util.lang) for war in wars
    ]
    await util.dump_orjson("nice_war", all_war_data)


async def get_nice_events_from_raw(
    conn: AsyncConnection, util: ExportUtil, events: list[MstEvent]
) -> list[NiceEvent]:  # pragma: no cover
    return [
        await get_nice_event(conn, util.region, event.id, util.lang) for event in events
    ]


async def dump_nice_events(
    util: ExportUtil, all_event_data: list[NiceEvent]
) -> None:  # pragma: no cover
    await util.dump_orjson("nice_event", all_event_data)


async def util_get_nice_shops_from_raw(
    conn: AsyncConnection, util: ExportUtil, shops: list[MstShop]
) -> list[NiceShop]:  # pragma: no cover
    return await get_nice_shops_from_raw(conn, util.region, shops, util.lang)


async def dump_nice_shops(
    util: ExportUtil, all_shop_data: list[NiceShop]
) -> None:  # pragma: no cover
    await util.dump_orjson("nice_shop", all_shop_data)


async def dump_illustrators(
    util: ExportUtil, illustrators: list[MstIllustrator]
) -> None:  # pragma: no cover
    if util.region == Region.JP and util.lang == Language.en:
        mstIllustrators_en: list[MstIllustrator] = []
        for illustrator in illustrators:
            illustrator_en = illustrator.copy()
            illustrator_en.name = get_translation(Language.en, illustrator_en.name)
            mstIllustrators_en.append(illustrator_en)
        await util.dump_orjson("nice_illustrator", mstIllustrators_en)
    else:
        await util.dump_orjson("nice_illustrator", illustrators)


async def dump_cvs(util: ExportUtil, cvs: list[MstCv]) -> None:  # pragma: no cover
    if util.region == Region.JP and util.lang == Language.en:
        mstCvs_en: list[MstCv] = []
        for cv in cvs:
            cv_en = cv.copy()
            cv_en.name = get_translation(Language.en, cv_en.name)
            mstCvs_en.append(cv_en)
        await util.dump_orjson("nice_cv", mstCvs_en)
    else:
        await util.dump_orjson("nice_cv", cvs)


async def dump_basic_servants(
    util: ExportUtil, file_name: str, svts: list[MstSvt]
) -> None:  # pragma: no cover
    all_basic_servant_data = sorted(
        await get_all_basic_servants(util.redis, util.region, util.lang, svts),
        key=lambda x: x.collectionNo,
    )
    await util.dump_orjson(file_name, all_basic_servant_data)


async def dump_basic_equips(
    util: ExportUtil, equips: list[MstSvt]
) -> None:  # pragma: no cover
    all_basic_equip_data = sorted(
        await get_all_basic_equips(util.redis, util.region, util.lang, equips),
        key=lambda x: x.collectionNo,
    )
    await util.dump_orjson("basic_equip", all_basic_equip_data)


async def dump_basic_mcs(
    util: ExportUtil, mcs: list[MstEquip]
) -> None:  # pragma: no cover
    all_basic_mc_data = get_all_basic_mcs(util.region, util.lang, mcs)
    await util.dump_orjson("basic_mystic_code", all_basic_mc_data)


async def dump_basic_ccs(
    util: ExportUtil, ccs: list[MstCommandCode]
) -> None:  # pragma: no cover
    all_basic_cc_data = sorted(
        get_all_basic_ccs(util.region, util.lang, ccs), key=lambda x: x.collectionNo
    )
    await util.dump_orjson("basic_command_code", all_basic_cc_data)


async def dump_basic_events(
    util: ExportUtil, events: list[MstEvent]
) -> None:  # pragma: no cover
    all_basic_event_data = get_all_basic_events(util.lang, events)
    await util.dump_orjson("basic_event", all_basic_event_data)


async def dump_basic_wars(
    util: ExportUtil, wars: list[MstWar]
) -> None:  # pragma: no cover
    all_basic_war_data = get_all_basic_wars(util.lang, wars)
    await util.dump_orjson("basic_war", all_basic_war_data)


SECS_PER_DAY = 3600 * 24


def is_recent(
    now: int, startedAt: int, endedAt: int, finishedAt: int | None, pre: int, delay: int
) -> bool:
    if finishedAt and finishedAt < endedAt:
        finishedAt = None
    if startedAt > now + pre * SECS_PER_DAY:
        return False
    if (finishedAt or endedAt) > now + 360 * SECS_PER_DAY:
        return now < startedAt + 7 * SECS_PER_DAY
    if finishedAt and finishedAt > endedAt and finishedAt < endedAt + 30 * SECS_PER_DAY:
        return now < finishedAt
    else:
        return now < endedAt + delay * SECS_PER_DAY


class TimerData(BaseModelORJson):
    updatedAt: int
    hash: str | None
    timestamp: int | None
    events: list[NiceEvent]
    gachas: list[NiceGacha]
    masterMissions: list[NiceMasterMission]
    shops: list[NiceShop]
    items: list[NiceItem]
    constants: dict[str, int]


async def dump_current_events(
    util: ExportUtil,
    repo_info: RepoInfo | None,
    nice_events: list[NiceEvent],
    raw_gacha_entities: list[GachaEntity],
    nice_mms: list[NiceMasterMission],
    nice_shops: list[NiceShop],
    nice_items: list[NiceItem],
    raw_constants: list[MstConstant],
) -> None:  # pragma: no cover
    now = int(time.time())

    events = [
        event
        for event in nice_events
        if is_recent(now, event.startedAt, event.endedAt, event.finishedAt, 14, 3)
    ]
    recent_gacha_entities = [
        g
        for g in raw_gacha_entities
        if is_recent(now, g.mstGacha.openedAt, g.mstGacha.closedAt, None, 14, 3)
        or (g.mstGacha.openedAt < now < g.mstGacha.closedAt)
    ]
    nice_gachas = get_all_nice_gachas(recent_gacha_entities, util.lang)
    masterMissions: list[NiceMasterMission] = []
    for mm in nice_mms:
        if mm.id == 10001:
            masterMissions.append(mm)
            continue
        if mm.id // 100000 == 3 and mm.id < 300010:
            continue
        if (
            is_recent(now, mm.startedAt, mm.endedAt, None, 14, 0)
            and mm.endedAt < now + 360 * SECS_PER_DAY
        ):
            masterMissions.append(mm)

    shops = [
        shop
        for shop in nice_shops
        if is_recent(now, shop.openedAt, shop.closedAt, None, 14, 0)
    ]
    items = [
        item
        for item in nice_items
        if item.type in (NiceItemType.continueItem, NiceItemType.friendshipUpItem)
        and is_recent(now, item.startedAt, item.endedAt, None, 14, 0)
    ]

    timer_data = TimerData(
        updatedAt=now,
        hash=repo_info.hash if repo_info else None,
        timestamp=repo_info.timestamp if repo_info else None,
        events=events,
        gachas=nice_gachas,
        masterMissions=masterMissions,
        shops=shops,
        items=items,
        constants={
            raw_constant.name: raw_constant.value for raw_constant in raw_constants
        },
    )

    await util.dump_orjson_object("timer_data", timer_data)


async def generate_exports(
    redis: Redis,
    region_path: dict[Region, DirectoryPath],
    async_engines: dict[Region, AsyncEngine],
    enable_webhook: bool,
) -> None:  # pragma: no cover
    if settings.export_all_nice:
        await export_constants(region_path)
        for region in region_path:
            start_time = time.perf_counter()
            export_path = project_root / "export" / region.value
            engine = async_engines[region]

            logger.info(f"Exporting {region} data …")
            util = ExportUtil(redis, region, export_path)

            async with engine.connect() as conn:
                all_svts = await fetch.get_everything(conn, MstSvt)

            all_servants = [
                svt for svt in all_svts if svt.collectionNo != 0 and svt.isServant()
            ]
            all_nice_servants = [
                svt
                for svt in all_svts
                if (svt.collectionNo != 0 and svt.isServant())
                or svt.id in EXTRA_SVT_ID_IN_NICE
            ]
            await dump_basic_servants(util, "basic_servant", all_servants)

            all_equips = [
                svt for svt in all_svts if svt.collectionNo != 0 and svt.isEquip()
            ]
            await dump_basic_equips(util, all_equips)

            async with engine.connect() as conn:
                mstCcs = await fetch.get_everything(conn, MstCommandCode)
            await dump_basic_ccs(util, mstCcs)

            async with engine.connect() as conn:
                mstWars = await fetch.get_everything(conn, MstWar)
            await dump_basic_wars(util, mstWars)

            async with engine.connect() as conn:
                mstEvents = await fetch.get_everything(conn, MstEvent)
            await dump_basic_events(util, mstEvents)

            async with engine.connect() as conn:
                mstEquips = await fetch.get_everything(conn, MstEquip)
            await dump_basic_mcs(util, mstEquips)

            await dump_normal(export_path, "nice_trait", TRAIT_NAME)
            await dump_normal(export_path, "nice_enums", ALL_ENUMS)

            async with engine.connect() as conn:
                mstIllustrators = await fetch.get_everything(conn, MstIllustrator)
            await dump_illustrators(util, mstIllustrators)

            async with engine.connect() as conn:
                mstCvs = await fetch.get_everything(conn, MstCv)
            await dump_cvs(util, mstCvs)

            async with engine.connect() as conn:
                bgms = await get_all_bgm_entities(conn)
            async with engine.connect() as conn:
                mstItems = await fetch.get_everything(conn, MstItem)
            async with engine.connect() as conn:
                mstMasterMissions = await fetch.get_everything(conn, MstMasterMission)
            async with engine.connect() as conn:
                mstShops = await fetch.get_all(conn, MstShop, 0)
            async with engine.connect() as conn:
                mstEnemyMasters = await fetch.get_everything(conn, MstEnemyMaster)
            async with engine.connect() as conn:
                mstClassBoardBases = await fetch.get_everything(conn, MstClassBoardBase)
            async with engine.connect() as conn:
                mstGrandGraphs = await fetch.get_everything(conn, MstGrandGraph)

            async with engine.connect() as conn:
                asset_storage = await fetch.get_everything(conn, AssetStorageLine)
            await util.dump_orjson("asset_storage", asset_storage)

            await dump_basic_servants(util, "basic_svt", all_svts)

            nice_items = get_nice_items_from_raw(util, mstItems)
            await dump_nice_items(util, nice_items)
            async with engine.connect() as conn:
                await dump_nice_mcs(conn, util, mstEquips)
            async with engine.connect() as conn:
                await dump_nice_ccs(conn, util, mstCcs)
            async with engine.connect() as conn:
                nice_mms = await get_nice_mms_from_raw(conn, util, mstMasterMissions)
            await dump_nice_mms(util, nice_mms)
            await dump_nice_bgms(util, bgms)
            async with engine.connect() as conn:
                nice_shops = await util_get_nice_shops_from_raw(conn, util, mstShops)
            await dump_nice_shops(util, nice_shops)
            async with engine.connect() as conn:
                await dump_nice_enemy_masters(conn, util, mstEnemyMasters)
            async with engine.connect() as conn:
                await dump_nice_class_boards(conn, util, mstClassBoardBases)
            async with engine.connect() as conn:
                await dump_nice_grand_graphs(conn, util, mstGrandGraphs)

            async with engine.connect() as conn:
                raw_gacha_entities = await get_all_gacha_entities(conn)
            await dump_nice_gachas(util, raw_gacha_entities)

            util_en = ExportUtil(redis, region, export_path, Language.en)
            nice_items_lang_en: list[NiceItem] = []
            if region == Region.JP:
                await dump_basic_servants(util_en, "basic_servant", all_servants)
                await dump_basic_events(util_en, mstEvents)

            async with engine.connect() as conn:
                await dump_svt(conn, util, "nice_servant", all_nice_servants)
            async with engine.connect() as conn:
                await dump_svt(conn, util, "nice_equip", all_equips)

            async with engine.connect() as conn:
                await dump_nice_wars(conn, util, mstWars)
            async with engine.connect() as conn:
                nice_events = await get_nice_events_from_raw(conn, util, mstEvents)
            await dump_nice_events(util, nice_events)

            async with engine.connect() as conn:
                raw_constants = await fetch.get_everything(conn, MstConstant)

            repo_info = await get_repo_version(redis, region)
            if repo_info is None:
                info_path = export_path / "info.json"
                if info_path.exists():
                    repo_info = RepoInfo.model_validate(
                        orjson.loads(info_path.read_bytes())
                    )

            export_info = await get_region_version(redis, region)
            if export_info:
                await dump_normal(
                    export_path, "info", export_info.model_dump(mode="json")
                )

            await dump_current_events(
                util,
                repo_info,
                nice_events,
                raw_gacha_entities,
                nice_mms,
                nice_shops,
                nice_items,
                raw_constants,
            )

            if enable_webhook:
                await report_webhooks(region_path, "export")

            if region == Region.JP:
                await dump_basic_equips(util_en, all_equips)
                await dump_basic_ccs(util_en, mstCcs)
                await dump_basic_wars(util_en, mstWars)
                await dump_basic_mcs(util_en, mstEquips)

                await dump_illustrators(util_en, mstIllustrators)
                await dump_cvs(util_en, mstCvs)

                await dump_basic_servants(util_en, "basic_svt", all_svts)
                nice_items_lang_en = get_nice_items_from_raw(util_en, mstItems)
                await dump_nice_items(util_en, nice_items_lang_en)
                async with engine.connect() as conn:
                    await dump_nice_mcs(conn, util_en, mstEquips)
                async with engine.connect() as conn:
                    await dump_nice_ccs(conn, util_en, mstCcs)
                await dump_nice_bgms(util_en, bgms)
                async with engine.connect() as conn:
                    await dump_nice_class_boards(conn, util_en, mstClassBoardBases)
                await dump_nice_gachas(util_en, raw_gacha_entities)

                async with engine.connect() as conn:
                    await dump_nice_wars(conn, util_en, mstWars)

                async with engine.connect() as conn:
                    nice_events_lang_en = await get_nice_events_from_raw(
                        conn, util_en, mstEvents
                    )
                await dump_nice_events(util_en, nice_events_lang_en)

                await dump_current_events(
                    util_en,
                    repo_info,
                    nice_events_lang_en,
                    raw_gacha_entities,
                    nice_mms,
                    nice_shops,
                    nice_items_lang_en,
                    raw_constants,
                )

            run_time = time.perf_counter() - start_time
            logger.info(f"Exported {region} data in {run_time:.2f}s.")


async def get_region_info(
    region: Region, region_folder: DirectoryPath
) -> dict[str, Any]:
    export_info: dict[str, Any] = {}
    app_info = get_app_info()
    export_info |= {
        "serverHash": app_info.hash,
        "serverTimestamp": app_info.timestamp,
    }

    if region in (Region.JP, Region.NA, Region.KR):
        with open(region_folder / "gamedatatop.json", "rb") as fp:
            gametop = orjson.loads(fp.read())
            response: dict[str, Any] = gametop["response"][0]["success"]
            export_info |= {
                "dataVer": response["dataVer"],
                "dateVer": response["dateVer"],
            }
        with open(region_folder / "metadata" / "assetbundle.json") as fp:
            export_info["assetbundle"] = orjson.loads(fp.read())

    return export_info


async def update_master_repo_info(
    redis: Redis, region_path: dict[Region, DirectoryPath]
) -> None:
    for region, gamedata in region_path.items():
        if (gamedata / ".git").exists():
            repo = Repo(gamedata)
            latest_commit = repo.commit()
            repo_info = RepoInfo(
                hash=latest_commit.hexsha[:6],
                timestamp=latest_commit.committed_date,  # pyright: ignore reportGeneralTypeIssues
            )
            await set_repo_version(redis, region, repo_info)

            region_info = await get_region_info(region, gamedata)
            region_info = repo_info.model_dump(mode="json") | region_info
            await set_region_version(
                redis, region, RegionInfo.model_validate(region_info)
            )


async def clear_redis_cache(
    redis: Redis,
    region_path: dict[Region, DirectoryPath],
    clear_heavy_quests: bool = False,
) -> None:  # pragma: no cover
    key_count = 0

    for region in region_path:
        key_pattern = f"{settings.redis_prefix}:cache:{region.value}*"
        async for key in redis.scan_iter(match=key_pattern):
            if (clear_heavy_quests and b"heavy" in key) or (
                not clear_heavy_quests and b"heavy" not in key
            ):
                if clear_heavy_quests:
                    while (load := psutil.cpu_percent()) > 25:
                        logger.warning(f"Load too heavy {load}")
                        await asyncio.sleep(15)

                await redis.delete(key)
                key_count += 1

                if clear_heavy_quests:
                    await asyncio.sleep(5)

    async for key in redis.scan_iter(match=f"{settings.redis_prefix}:cache::*"):
        await redis.delete(key)
        key_count += 1

    logger.info(f"Cleared {key_count} cache redis keys. {clear_heavy_quests=}")


async def load_svt_extra(
    redis: Redis, region_path: dict[Region, DirectoryPath]
) -> None:  # pragma: no cover
    logger.info("Loading extra svt data …")
    start_loading_time = time.perf_counter()

    for region, gamedata_path in region_path.items():
        svtExtras = get_extra_svt_data(region, gamedata_path)
        if settings.write_postgres_data:
            with engines[region].begin() as conn:
                load_pydantic_to_db(conn, svtExtras, mstSvtExtra)
        if settings.write_redis_data:
            await load_svt_extra_redis(redis, region, svtExtras)

    extra_loading_time = time.perf_counter() - start_loading_time
    logger.info(f"Loaded extra svt data in {extra_loading_time:.2f}s.")


async def load_and_export(
    redis: Redis,
    region_path: dict[Region, DirectoryPath],
    async_engines: dict[Region, AsyncEngine],
    enable_webhook: bool,
) -> None:  # pragma: no cover
    try:
        if settings.write_postgres_data:
            update_db(region_path)
        if settings.write_redis_data:
            await load_redis_data(redis, region_path)
            await update_master_repo_info(redis, region_path)
        if settings.write_postgres_data or settings.write_redis_data:
            await load_svt_extra(redis, region_path)
            if enable_webhook:
                await report_webhooks(region_path, "load")
    except Exception:  # noqa: BLE001
        logger.exception("Failed to load data")

    if settings.clear_redis_cache:
        await clear_redis_cache(redis, region_path, clear_heavy_quests=False)

    if settings.export_all_nice:
        try:
            enable_webhook_jp = enable_webhook and set(region_path) == {Region.JP}
            await generate_exports(redis, region_path, async_engines, enable_webhook_jp)
            if enable_webhook and not enable_webhook_jp:
                await report_webhooks(region_path, "export")
        except Exception:  # noqa: BLE001
            logger.exception("Failed to export data")

    if settings.clear_redis_cache:
        await clear_redis_cache(redis, region_path, clear_heavy_quests=True)


def update_data_repo(
    region_path: dict[Region, DirectoryPath],
) -> None:  # pragma: no cover
    try:
        if settings.github_webhook_git_pull:
            for gamedata in region_path.values():
                if (gamedata / ".git").exists():
                    repo = Repo(gamedata)
                    for fetch_info in repo.remotes[0].pull():
                        commit_hash = fetch_info.commit.hexsha[:6]
                        logger.info(f"Updated {fetch_info.ref} to {commit_hash}")
    except Exception:  # noqa: BLE001
        logger.exception("Failed to pull data")


async def report_webhooks(
    region_path: dict[Region, DirectoryPath],
    event: str,
) -> None:  # pragma: no cover
    async with httpx.AsyncClient() as client:
        for index, url in enumerate(settings.webhooks):
            try:
                await client.post(
                    url, json={"regions": list(region_path.keys()), "event": event}
                )
            except Exception:  # noqa: BLE001
                logger.exception(f"Failed to report webhook {index}")


async def pull_and_update(
    region_path: dict[Region, DirectoryPath],
    async_engines: dict[Region, AsyncEngine],
    redis: Redis,
) -> None:  # pragma: no cover
    await run_in_threadpool(lambda: update_data_repo(region_path))
    await load_and_export(redis, region_path, async_engines, True)
