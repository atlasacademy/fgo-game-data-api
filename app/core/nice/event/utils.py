from dataclasses import dataclass

from ....schemas.common import Region
from ....schemas.gameenums import COMMON_CONSUME_TYPE_NAME
from ....schemas.nice import NiceCommonConsume, NiceGift, NiceVoiceGroup, NiceVoiceLine
from ....schemas.raw import MstCommonConsume, MstGift, MstGiftAdd
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


@dataclass
class GiftData:
    gift_adds: list[MstGiftAdd]
    gift_maps: dict[int, list[MstGift]]


def get_nice_gifts(region: Region, gift_id: int, gift_data: GiftData) -> list[NiceGift]:
    return [
        get_nice_gift(region, gift, gift_data.gift_adds, gift_data.gift_maps)
        for gift in gift_data.gift_maps[gift_id]
    ]


def get_nice_common_consume(common_consume: MstCommonConsume) -> NiceCommonConsume:
    return NiceCommonConsume(
        id=common_consume.id,
        priority=common_consume.priority,
        type=COMMON_CONSUME_TYPE_NAME[common_consume.type],
        objectId=common_consume.objectId,
        num=common_consume.num,
    )
