from ....schemas.nice import NiceSvtScript
from ....schemas.raw import MstSvtScript, MstSvtScriptExtendData


def get_nice_chara_script(script: MstSvtScript) -> NiceSvtScript:
    return NiceSvtScript(
        id=script.id,
        form=script.form,
        faceX=script.faceX,
        faceY=script.faceY,
        extendData=MstSvtScriptExtendData.model_validate(script.extendData),
        bgImageId=script.bgImageId,
        scale=script.scale,
        offsetX=script.offsetX,
        offsetY=script.offsetY,
        offsetXMyroom=script.offsetXMyroom,
        offsetYMyroom=script.offsetYMyroom,
        svtId=script.svtId,
        limitCount=script.limitCount,
    )
