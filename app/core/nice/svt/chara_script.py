from typing import Any

from ....schemas.nice import NiceSvtScript
from ....schemas.raw import MstSvtScript, MstSvtScriptExtendData
from ...raw import fix_script_extend_data


def get_nice_extend_data(data: dict[str, Any]) -> MstSvtScriptExtendData:
    return MstSvtScriptExtendData.model_validate(fix_script_extend_data(data))


def get_nice_chara_script(script: MstSvtScript) -> NiceSvtScript:
    return NiceSvtScript(
        id=script.id,
        form=script.form,
        faceX=script.faceX,
        faceY=script.faceY,
        extendData=get_nice_extend_data(script.extendData),
        bgImageId=script.bgImageId,
        scale=script.scale,
        offsetX=script.offsetX,
        offsetY=script.offsetY,
        offsetXMyroom=script.offsetXMyroom,
        offsetYMyroom=script.offsetYMyroom,
        svtId=script.svtId,
        limitCount=script.limitCount,
    )
