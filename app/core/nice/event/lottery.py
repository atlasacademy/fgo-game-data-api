from ....config import Settings
from ....schemas.common import Region
from ....schemas.gameenums import PAY_TYPE_NAME, BoxGachaFlag
from ....schemas.nice import (
    AssetURL,
    NiceEventLottery,
    NiceEventLotteryBox,
    NiceEventLotteryTalk,
    NiceItem,
    NiceItemAmount,
    NiceVoiceGroup,
)
from ....schemas.raw import (
    MstBoxGacha,
    MstBoxGachaBase,
    MstBoxGachaTalk,
    MstEventRewardScene,
)
from ...utils import fmt_url
from ..gift import GiftData, get_nice_gifts
from .utils import get_voice_lines


settings = Settings()


def get_nice_lottery_box(
    region: Region,
    box: MstBoxGachaBase,
    box_index: int,
    talk_id: int,
    gift_data: GiftData,
) -> NiceEventLotteryBox:
    base_settings = {"base_url": settings.asset_url, "region": region}
    return NiceEventLotteryBox(
        id=box.id,
        boxIndex=box_index,
        talkId=talk_id,
        no=box.no,
        type=box.type,
        gifts=get_nice_gifts(region, box.targetId, gift_data),
        maxNum=box.maxNum,
        isRare=box.isRare,
        priority=box.priority,
        detail=box.detail,
        icon=fmt_url(
            AssetURL.eventReward,
            **base_settings,
            fname=f"icon_event_{box.iconId}",
        ),
        banner=fmt_url(
            AssetURL.eventReward,
            **base_settings,
            fname=f"event_gachabanner_{box.bannerId}",
        ),
    )


def get_nice_lottery_talk(
    gacha_talk: MstBoxGachaTalk,
    voice_groups: list[NiceVoiceGroup],
    reward_scene_guide_id: int | None = None,
) -> NiceEventLotteryTalk:
    guide_id = gacha_talk.guideImageId
    if gacha_talk.guideImageId == 0 and reward_scene_guide_id is not None:
        guide_id = reward_scene_guide_id

    return NiceEventLotteryTalk(
        talkId=gacha_talk.id,
        no=gacha_talk.no,
        guideImageId=guide_id,
        beforeVoiceLines=get_voice_lines(
            voice_groups, guide_id, gacha_talk.befVoiceIds
        ),
        afterVoiceLines=get_voice_lines(voice_groups, guide_id, gacha_talk.aftVoiceIds),
        isRare=gacha_talk.isRare,
    )


def get_nice_lottery(
    region: Region,
    lottery: MstBoxGacha,
    boxes: list[MstBoxGachaBase],
    lottery_talks: list[MstBoxGachaTalk],
    gift_data: GiftData,
    item_map: dict[int, NiceItem],
    reward_scenes: list[MstEventRewardScene],
    voice_groups: list[NiceVoiceGroup],
) -> NiceEventLottery:
    nice_boxes: list[NiceEventLotteryBox] = []
    for box_index, base_id in enumerate(lottery.baseIds):
        for box in boxes:
            if box.id == base_id:
                nice_boxes.append(
                    get_nice_lottery_box(
                        region, box, box_index, lottery.talkIds[box_index], gift_data
                    )
                )

    reward_scene_guide_id: int | None = None
    for reward_scene in reward_scenes:
        if lottery.slot == reward_scene.slot and reward_scene.guideImageIds:
            reward_scene_guide_id = reward_scene.guideImageIds[0]
            break

    return NiceEventLottery(
        id=lottery.id,
        slot=lottery.slot,
        payType=PAY_TYPE_NAME[lottery.payType],
        cost=NiceItemAmount(
            item=item_map[lottery.payTargetId],
            amount=lottery.payValue,
        ),
        priority=lottery.priority,
        limited=lottery.flag == BoxGachaFlag.LIMIT_RESET,
        boxes=nice_boxes,
        talks=[
            get_nice_lottery_talk(lottery_talk, voice_groups, reward_scene_guide_id)
            for lottery_talk in lottery_talks
        ],
    )
