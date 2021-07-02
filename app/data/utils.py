from typing import Type, TypeVar

import orjson
from pydantic.types import DirectoryPath

from ..schemas.base import BaseModelORJson
from ..schemas.raw import (
    MstEvent,
    MstEventMissionCondition,
    MstEventMissionConditionDetail,
    MstShop,
    MstShopRelease,
    MstSkill,
    MstSvt,
    MstSvtComment,
    MstSvtExtra,
    MstSvtLimitAdd,
    MstSvtSkill,
    MstWar,
)


PydanticModel = TypeVar("PydanticModel", bound=BaseModelORJson)


MODEL_FILE_NAME: dict[Type[BaseModelORJson], str] = {
    MstEvent: "mstEvent",
    MstShop: "mstShop",
    MstSkill: "mstSkill",
    MstSvt: "mstSvt",
    MstSvtLimitAdd: "mstSvtLimitAdd",
    MstSvtComment: "mstSvtComment",
    MstSvtExtra: "mstSvtExtra",
    MstSvtSkill: "mstSvtSkill",
    MstShopRelease: "mstShopRelease",
    MstWar: "mstWar",
    MstEventMissionCondition: "mstEventMissionCondition",
    MstEventMissionConditionDetail: "mstEventMissionConditionDetail",
}


def load_master_data(
    gamedata_path: DirectoryPath, model: Type[PydanticModel]
) -> list[PydanticModel]:
    file_name = MODEL_FILE_NAME[model]
    with open(gamedata_path / "master" / f"{file_name}.json", "rb") as fp:
        data = orjson.loads(fp.read())
    return [model.parse_obj(item) for item in data]
