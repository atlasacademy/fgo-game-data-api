from ....schemas.gameenums import COMMON_CONSUME_TYPE_NAME
from ....schemas.nice import NiceCommonConsume, NiceGift, NiceVoiceGroup, NiceVoiceLine
from ....schemas.raw import MstCommonConsume, MstGift
from ..gift import get_nice_gift


def get_voice_lines(
    voice_groups: list[NiceVoiceGroup], svt_id: int, voice_ids: list[str]
) -> list[NiceVoiceLine]:
    return [
        voice_line
        for voice_group in voice_groups
        for voice_line in voice_group.voiceLines
        if voice_group.svtId == svt_id and set(voice_ids).intersection(voice_line.id)
    ]


def get_nice_gifts(gift_id: int, gift_maps: dict[int, list[MstGift]]) -> list[NiceGift]:
    return [get_nice_gift(gift) for gift in gift_maps[gift_id]]


def get_nice_common_consume(common_consume: MstCommonConsume) -> NiceCommonConsume:
    return NiceCommonConsume(
        id=common_consume.id,
        priority=common_consume.priority,
        type=COMMON_CONSUME_TYPE_NAME[common_consume.type],
        objectId=common_consume.objectId,
        num=common_consume.num,
    )
