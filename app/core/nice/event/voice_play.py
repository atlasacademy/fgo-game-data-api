from ....schemas.gameenums import COND_TYPE_NAME
from ....schemas.nice import NiceEventVoicePlay, NiceVoiceGroup
from ....schemas.raw import MstEventVoicePlay
from .utils import get_voice_lines


def get_nice_event_voice_play(
    voice_play: MstEventVoicePlay, voice_groups: list[NiceVoiceGroup]
) -> NiceEventVoicePlay:
    return NiceEventVoicePlay(
        slot=voice_play.slot,
        idx=voice_play.idx,
        guideImageId=voice_play.guideImageId,
        voiceLines=get_voice_lines(
            voice_groups, voice_play.guideImageId, voice_play.voiceIds
        ),
        confirmVoiceLines=get_voice_lines(
            voice_groups, voice_play.guideImageId, voice_play.confirmVoiceIds
        ),
        condType=COND_TYPE_NAME[voice_play.condType],
        condValue=voice_play.condValue,
        startedAt=voice_play.startedAt,
        endedAt=voice_play.endedAt,
    )
