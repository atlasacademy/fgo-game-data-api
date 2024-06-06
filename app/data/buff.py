from pydantic import DirectoryPath

from ..schemas.gameenums import BuffConvertType
from ..schemas.raw import MstBuff, MstBuffConvert, MstClassRelationOverwrite
from .utils import load_master_data


def get_buff_with_classrelation(gamedata_path: DirectoryPath) -> dict[int, MstBuff]:
    mstBuffs = {buff.id: buff for buff in load_master_data(gamedata_path, MstBuff)}
    mstClassRelationOverwrites = load_master_data(
        gamedata_path, MstClassRelationOverwrite
    )
    mstBuffConvert = load_master_data(gamedata_path, MstBuffConvert)

    for buff in mstBuffs.values():
        if "relationId" in buff.script:
            overwrite_relation_id = int(buff.script["relationId"])
            overwrites = [
                overwrite.model_dump(mode="json")
                for overwrite in mstClassRelationOverwrites
                if overwrite.id == overwrite_relation_id
            ]
            buff.script["relationOverwrite"] = overwrites

    for convert in mstBuffConvert:
        if convert.buffId in mstBuffs:
            buff = mstBuffs[convert.buffId]
            convert_data = convert.model_dump(mode="json")
            if convert_data["convertType"] == BuffConvertType.BUFF:
                convert_data["targetBuffs"] = [
                    mstBuffs[buff_id] for buff_id in convert_data["targetIds"]
                ]
            convert_data["convertBuffs"] = [
                mstBuffs[buff_id] for buff_id in convert_data["convertBuffIds"]
            ]
            buff.script["convert"] = convert_data

    return mstBuffs
