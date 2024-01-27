import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, NamedTuple, Union

import aiofiles
from pydantic import DirectoryPath

from ..config import logger, project_root
from ..core.utils import get_traits_list
from ..schemas.common import Region
from ..schemas.enums import ATTRIBUTE_NAME, TRAIT_NAME, Trait, get_class_name
from ..schemas.gameenums import (
    AI_COND_CHECK_NAME,
    AI_COND_NAME,
    AI_COND_PARAMETER_NAME,
    AI_COND_REFINE_NAME,
    AI_COND_TARGET_NAME,
    BUFF_ACTION_NAME,
    BUFF_LIMIT_NAME,
    BUFF_TYPE_NAME,
    CARD_TYPE_NAME,
    GIFT_TYPE_NAME,
    SERVANT_FRAME_TYPE_NAME,
    AiCond,
    BuffAction,
)


def get_nice_constant(raw_data: Any) -> dict[str, int]:
    return {constant["name"]: constant["value"] for constant in raw_data}


def get_nice_constant_str(raw_data: Any) -> dict[str, str]:
    return {constant["name"]: constant["value"] for constant in raw_data}


def get_nice_gift(raw_gift: Any) -> dict[Any, Any]:
    return {
        "id": raw_gift["id"],
        "type": GIFT_TYPE_NAME[raw_gift["type"]],
        "objectId": raw_gift["objectId"],
        "priority": raw_gift["priority"],
        "num": raw_gift["num"],
    }


def get_nice_class(raw_data: Any) -> Any:
    return [
        {
            "id": class_data["id"],
            "className": get_class_name(class_data["id"]),
            "name": class_data["name"],
            "individuality": (
                TRAIT_NAME.get(class_data["individuality"], Trait.unknown)
                if class_data["individuality"]
                else Trait.unknown
            ),
            "attackRate": class_data["attackRate"],
            "imageId": class_data["imageId"],
            "iconImageId": class_data["iconImageId"],
            "frameId": class_data["frameId"],
            "priority": class_data["priority"],
            "groupType": class_data["groupType"],
            "relationId": class_data["relationId"],
            "supportGroup": class_data["supportGroup"],
            "autoSelSupportType": class_data["autoSelSupportType"],
        }
        for class_data in raw_data
    ]


def get_nice_attackrate(raw_data: Any) -> Any:
    return {
        get_class_name(class_data["id"]): class_data["attackRate"]
        for class_data in raw_data
    }


def get_nice_card_data(raw_data: Any) -> Any:
    out_data: dict[str, dict[int, Any]] = {}
    for card in raw_data:
        card_id = card["id"]
        card_index = card["num"]
        card["individuality"] = [
            trait.dict(exclude_unset=True)
            for trait in get_traits_list(card["individuality"])
        ]
        card.pop("id")
        card.pop("num")
        if card_id in CARD_TYPE_NAME:
            card_name = CARD_TYPE_NAME[card_id]
            if card_name in out_data:
                out_data[card_name][card_index] = card
            else:
                out_data[card_name] = {card_index: card}
    return out_data


def get_nice_attri_relation(raw_data: Any) -> Any:
    out_data: dict[str, dict[str, int]] = {}
    for attribute_relation in raw_data:
        atkAttri = ATTRIBUTE_NAME[attribute_relation["atkAttri"]]
        defAttri = ATTRIBUTE_NAME[attribute_relation["defAttri"]]
        attackRate = attribute_relation["attackRate"]
        if atkAttri in out_data:
            out_data[atkAttri][defAttri] = attackRate
        else:
            out_data[atkAttri] = {defAttri: attackRate}
    return out_data


def get_nice_class_relation(raw_data: Any) -> Any:
    out_data: dict[str, dict[str, int]] = {}
    for class_relation in raw_data:
        atkAttri = get_class_name(class_relation["atkClass"])
        defAttri = get_class_name(class_relation["defClass"])
        if atkAttri and defAttri:
            attackRate = class_relation["attackRate"]
            if atkAttri in out_data:
                out_data[atkAttri][defAttri] = attackRate
            else:
                out_data[atkAttri] = {defAttri: attackRate}
    return out_data


def get_nice_svt_exceed(raw_data: Any) -> Any:
    def find_previous_exceed_qp(rarity: int, exceed: int) -> int:
        previous_exceed = next(
            svt_exceed
            for svt_exceed in raw_data
            if svt_exceed["rarity"] == rarity
            and svt_exceed["exceedCount"] == exceed - 1
        )
        previous_exceed_qp: int = previous_exceed["qp"]
        return previous_exceed_qp

    out_data: dict[int, dict[int, dict[str, Union[int, str]]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    for svtExceed in raw_data:
        if svtExceed["exceedCount"] != 0:
            out_data[svtExceed["rarity"]][svtExceed["exceedCount"]] = {
                "qp": find_previous_exceed_qp(
                    svtExceed["rarity"], svtExceed["exceedCount"]
                ),
                "addLvMax": svtExceed["addLvMax"],
                "frameType": SERVANT_FRAME_TYPE_NAME[svtExceed["frameType"]],
            }

    return out_data


def get_nice_buff_action(raw_data: Any) -> Any:
    def get_max_rate(buff_types: list[int]) -> list[int]:
        return list(
            {buff["maxRate"] for buff in raw_data if buff["type"] in buff_types}
        )

    with open(
        project_root / "export" / "BuffList.ActionList.json", "r", encoding="utf-8"
    ) as fp:
        data = json.load(fp)

    out_data = {}

    for buff_action in data:
        out_item = data[buff_action]
        out_item["limit"] = BUFF_LIMIT_NAME[out_item["limit"]]
        out_item["maxRate"] = get_max_rate(
            out_item["plusTypes"] + out_item["minusTypes"]
        )
        out_item["plusTypes"] = [
            BUFF_TYPE_NAME[bufft] for bufft in out_item["plusTypes"]
        ]
        out_item["minusTypes"] = [
            BUFF_TYPE_NAME[bufft] for bufft in out_item["minusTypes"]
        ]
        out_data[BUFF_ACTION_NAME[BuffAction[buff_action].value]] = out_item
    return out_data


async def get_nice_ai_cond(region: Region, export_path: Path) -> None:
    async with aiofiles.open(
        export_path / "AiConditionInformation.json", "r", encoding="utf-8"
    ) as fp:
        data = json.loads(await fp.read())

    out_data = {}

    for ai_cond in data:
        out_item = data[ai_cond]
        out_item["target"] = AI_COND_TARGET_NAME[out_item["target"]]
        out_item["paramater"] = AI_COND_PARAMETER_NAME[out_item["paramater"]]
        out_item["check"] = AI_COND_CHECK_NAME[out_item["check"]]
        out_item["refine"] = AI_COND_REFINE_NAME[out_item["refine"]]
        out_data[AI_COND_NAME[AiCond[ai_cond].value]] = out_item

    export_file = export_path / region.value / "NiceAiConditionInformation.json"
    async with aiofiles.open(export_file, "w", encoding="utf-8") as fp:
        await fp.write(json.dumps(out_data, ensure_ascii=False, indent=2))


class ExportParam(NamedTuple):
    input: str
    converter: Callable[[Any], Any]
    output: str


TO_EXPORT = [
    ExportParam(
        input="mstConstant", converter=get_nice_constant, output="NiceConstant"
    ),
    ExportParam(
        input="mstConstantStr",
        converter=get_nice_constant_str,
        output="NiceConstantStr",
    ),
    ExportParam(
        input="mstClass",
        converter=get_nice_class,
        output="NiceClass",
    ),
    ExportParam(
        input="mstClass", converter=get_nice_attackrate, output="NiceClassAttackRate"
    ),
    ExportParam(input="mstCard", converter=get_nice_card_data, output="NiceCard"),
    ExportParam(
        input="mstAttriRelation",
        converter=get_nice_attri_relation,
        output="NiceAttributeRelation",
    ),
    ExportParam(
        input="mstClassRelation",
        converter=get_nice_class_relation,
        output="NiceClassRelation",
    ),
    ExportParam(
        input="mstBuff",
        converter=get_nice_buff_action,
        output="NiceBuffList.ActionList",
    ),
    ExportParam(
        input="mstSvtExceed",
        converter=get_nice_svt_exceed,
        output="NiceSvtGrailCost",
    ),
]


async def export_constant(region: Region, master_path: Path, export_path: Path) -> None:
    for export in TO_EXPORT:
        logger.info(f"Exporting {export.input} ...")
        async with aiofiles.open(
            master_path / "master" / f"{export.input}.json", "r", encoding="utf-8"
        ) as fp:
            raw_data = json.loads(await fp.read())
        export_file = export_path / region.value / f"{export.output}.json"
        async with aiofiles.open(export_file, "w", encoding="utf-8") as fp:
            await fp.write(
                json.dumps(export.converter(raw_data), ensure_ascii=False, indent=2)
            )


async def export_nice_master_lvl(
    region: Region, master_path: Path, export_path: Path
) -> Any:
    logger.info("Exporting nice master level ...")
    constant_path = export_path / region.value / f"{TO_EXPORT[0].output}.json"
    async with aiofiles.open(constant_path, "r", encoding="utf-8") as fp:
        constant = json.loads(await fp.read())
    async with aiofiles.open(
        master_path / "master" / "mstUserExp.json", "r", encoding="utf-8"
    ) as fp:
        mstUserExp: list[dict[str, int]] = json.loads(await fp.read())
    async with aiofiles.open(
        master_path / "master" / "mstGift.json", "r", encoding="utf-8"
    ) as fp:
        mstGiftId: dict[int, dict[str, int]] = {
            gift["id"]: gift for gift in json.loads(await fp.read())
        }

    def get_current_value(base: int, key: str, current: int) -> int:
        return base + sum(user_exp[key] for user_exp in mstUserExp[: current + 1])

    def get_total_exp(current: int) -> int:
        if current == 0:
            return 0
        else:
            return mstUserExp[current - 1]["exp"]

    nice_data = {
        lvl["lv"]: {
            "requiredExp": get_total_exp(lvli),
            "maxAp": get_current_value(constant["USER_ACT"], "addActMax", lvli),
            "maxCost": get_current_value(constant["USER_COST"], "addCostMax", lvli),
            "maxFriend": get_current_value(
                constant["FRIEND_NUM"], "addFriendMax", lvli
            ),
            "gift": (
                get_nice_gift(mstGiftId[lvl["giftId"]]) if lvl["giftId"] != 0 else None
            ),
        }
        for lvli, lvl in enumerate(mstUserExp)
    }

    export_file = export_path / region.value / "NiceUserLevel.json"
    async with aiofiles.open(export_file, "w", encoding="utf-8") as fp:
        await fp.write(json.dumps(nice_data, ensure_ascii=False, indent=2))


async def export_constants(region_path: dict[Region, DirectoryPath]) -> None:
    export_path = project_root / "export"
    for region, path in region_path.items():
        logger.info(f"Export {region} constants")
        await export_constant(region, path, export_path)
        await export_nice_master_lvl(region, path, export_path)
        await get_nice_ai_cond(region, export_path)
