from typing import Type, TypeVar

import orjson
from pydantic import DirectoryPath

from ..schemas.base import BaseModelORJson
from ..schemas.raw import (
    MstAi,
    MstAiAct,
    MstBgm,
    MstBuff,
    MstBuffConvert,
    MstClassRelationOverwrite,
    MstCombineAppendPassiveSkill,
    MstCombineCostume,
    MstCombineLimit,
    MstCombineSkill,
    MstCommandCode,
    MstCommandCodeSkill,
    MstEquip,
    MstEquipSkill,
    MstEvent,
    MstEventMissionCondition,
    MstEventMissionConditionDetail,
    MstFunc,
    MstGift,
    MstGiftAdd,
    MstItem,
    MstItemSelect,
    MstShop,
    MstShopRelease,
    MstShopScript,
    MstSkill,
    MstSkillLv,
    MstSvt,
    MstSvtAppendPassiveSkill,
    MstSvtComment,
    MstSvtCostume,
    MstSvtExtra,
    MstSvtLimit,
    MstSvtLimitAdd,
    MstSvtPassiveSkill,
    MstSvtSkill,
    MstSvtTreasureDevice,
    MstSvtVoice,
    MstTreasureDevice,
    MstTreasureDeviceLv,
    MstVoice,
    MstWar,
)


PydanticModel = TypeVar("PydanticModel", bound=BaseModelORJson)


MODEL_FILE_NAME: dict[Type[BaseModelORJson], str] = {
    MstAi: "mstAi",
    MstAiAct: "mstAiAct",
    MstBuff: "mstBuff",
    MstClassRelationOverwrite: "mstClassRelationOverwrite",
    MstCombineAppendPassiveSkill: "mstCombineAppendPassiveSkill",
    MstCombineCostume: "mstCombineCostume",
    MstCombineLimit: "mstCombineLimit",
    MstCombineSkill: "mstCombineSkill",
    MstCommandCode: "mstCommandCode",
    MstCommandCodeSkill: "mstCommandCodeSkill",
    MstEquip: "mstEquip",
    MstEquipSkill: "mstEquipSkill",
    MstEvent: "mstEvent",
    MstEventMissionCondition: "mstEventMissionCondition",
    MstEventMissionConditionDetail: "mstEventMissionConditionDetail",
    MstFunc: "mstFunc",
    MstGift: "mstGift",
    MstGiftAdd: "mstGiftAdd",
    MstItem: "mstItem",
    MstItemSelect: "mstItemSelect",
    MstShop: "mstShop",
    MstShopRelease: "mstShopRelease",
    MstShopScript: "mstShopScript",
    MstSkill: "mstSkill",
    MstSkillLv: "mstSkillLv",
    MstSvt: "mstSvt",
    MstSvtAppendPassiveSkill: "mstSvtAppendPassiveSkill",
    MstSvtComment: "mstSvtComment",
    MstSvtCostume: "mstSvtCostume",
    MstSvtExtra: "mstSvtExtra",
    MstSvtLimit: "mstSvtLimit",
    MstSvtLimitAdd: "mstSvtLimitAdd",
    MstSvtPassiveSkill: "mstSvtPassiveSkill",
    MstSvtSkill: "mstSvtSkill",
    MstSvtTreasureDevice: "mstSvtTreasureDevice",
    MstSvtVoice: "mstSvtVoice",
    MstTreasureDevice: "mstTreasureDevice",
    MstTreasureDeviceLv: "mstTreasureDeviceLv",
    MstVoice: "mstVoice",
    MstWar: "mstWar",
    MstBuffConvert: "mstBuffConvert",
    MstBgm: "mstBgm",
}


def load_master_data(
    gamedata_path: DirectoryPath, model: Type[PydanticModel]
) -> list[PydanticModel]:
    file_name = MODEL_FILE_NAME[model]
    file_loc = gamedata_path / "master" / f"{file_name}.json"

    if not file_loc.exists():
        return []

    with open(file_loc, "rb") as fp:
        data = orjson.loads(fp.read())
    return [model.model_validate(item) for item in data]
