from pydantic import DirectoryPath

from ..schemas.raw import MstBuff, MstClassRelationOverwrite
from .utils import load_master_data


def get_buff_with_classrelation(gamedata_path: DirectoryPath) -> list[MstBuff]:
    mstBuffs = load_master_data(gamedata_path, MstBuff)
    mstClassRelationOverwrites = load_master_data(
        gamedata_path, MstClassRelationOverwrite
    )

    for buff in mstBuffs:
        if "relationId" in buff.script:
            overwrite_relation_id = int(buff.script["relationId"])
            overwrites = [
                overwrite.dict()
                for overwrite in mstClassRelationOverwrites
                if overwrite.id == overwrite_relation_id
            ]
            buff.script["relationOverwrite"] = overwrites

    return mstBuffs
