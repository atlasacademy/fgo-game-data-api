from typing import Dict, List

from ....config import Settings
from ....data.gamedata import masters
from ....schemas.common import Region
from ....schemas.enums import (
    COND_TYPE_NAME,
    VOICE_COND_NAME,
    VOICE_TYPE_NAME,
    SvtVoiceType,
    VoiceCondType,
)
from ....schemas.nice import AssetURL, NiceVoiceCond, NiceVoiceGroup, NiceVoiceLine
from ....schemas.raw import (
    GlobalNewMstSubtitle,
    MstSvtVoice,
    ScriptJson,
    ScriptJsonCond,
)
from ...utils import nullable_to_string


settings = Settings()


def get_voice_folder(voice_type: int) -> str:
    if voice_type == SvtVoiceType.BATTLE:
        return "Servants_"
    elif voice_type == SvtVoiceType.TREASURE_DEVICE:
        return "NoblePhantasm_"
    else:
        return "ChrVoice_"


def get_voice_url(region: Region, svt_id: int, voice_type: int, voice_id: str) -> str:
    folder = get_voice_folder(voice_type) + str(svt_id)
    return AssetURL.audio.format(
        base_url=settings.asset_url, region=region, folder=folder, id=voice_id
    )


def get_nice_voice_cond(
    region: Region, cond: ScriptJsonCond, costume_ids: Dict[int, int]
) -> NiceVoiceCond:
    cond_value = (
        costume_ids[cond.value]
        if cond.condType == VoiceCondType.COSTUME
        else cond.value
    )

    cond_value_list = (
        [group.svtId for group in masters[region].mstSvtGroupId[cond.value]]
        if cond.condType == VoiceCondType.SVT_GROUP
        else []
    )

    voice_cond = NiceVoiceCond(
        condType=VOICE_COND_NAME[cond.condType],
        eventId=cond.eventId,
        value=cond_value,
        valueList=cond_value_list,
    )

    return voice_cond


def get_nice_voice_line(
    region: Region,
    script: ScriptJson,
    svt_id: int,
    voice_type: int,
    costume_ids: Dict[int, int],
    subtitle_ids: Dict[str, str],
) -> NiceVoiceLine:
    first_voice_id = script.infos[0].id

    voice_line = NiceVoiceLine(
        overwriteName=nullable_to_string(script.overwriteName),
        id=(info.id for info in script.infos),
        audioAssets=(
            get_voice_url(region, svt_id, voice_type, info.id) for info in script.infos
        ),
        delay=(info.delay for info in script.infos),
        face=(info.face for info in script.infos),
        form=(info.form for info in script.infos),
        text=(nullable_to_string(info.text) for info in script.infos),
        conds=(get_nice_voice_cond(region, info, costume_ids) for info in script.conds),
        subtitle=subtitle_ids.get(str(svt_id) + "_" + first_voice_id, ""),
    )

    # Some voice lines have the first info id ending with xxx1 or xxx2 and we want xxx0
    voice_id = first_voice_id.split("_")[1][:-1] + "0"
    if voice_id in masters[region].mstVoiceId:
        mstVoice = masters[region].mstVoiceId[voice_id]
        voice_line.name = mstVoice.name
        voice_line.condType = COND_TYPE_NAME[mstVoice.condType]
        voice_line.condValue = mstVoice.condValue
        voice_line.priority = mstVoice.priority
        voice_line.svtVoiceType = VOICE_TYPE_NAME[mstVoice.svtVoiceType]

    return voice_line


def get_nice_voice_group(
    region: Region,
    voice: MstSvtVoice,
    costume_ids: Dict[int, int],
    subtitles: List[GlobalNewMstSubtitle],
) -> NiceVoiceGroup:

    subtitle_ids = {subtitle.id: subtitle.serif for subtitle in subtitles}

    return NiceVoiceGroup(
        svtId=voice.id,
        voicePrefix=voice.voicePrefix,
        type=VOICE_TYPE_NAME[voice.type],
        voiceLines=(
            get_nice_voice_line(
                region, script, voice.id, voice.type, costume_ids, subtitle_ids
            )
            for script in voice.scriptJson
        ),
    )
