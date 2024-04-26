from ....config import Settings
from ....schemas.common import Region
from ....schemas.nice import (
    AssetURL,
    NiceEventDigging,
    NiceEventDiggingBlock,
    NiceEventDiggingReward,
    NiceItem,
)
from ....schemas.raw import (
    MstCommonConsume,
    MstEventDigging,
    MstEventDiggingBlock,
    MstEventDiggingReward,
)
from ...utils import fmt_url
from ..gift import GiftData, get_nice_common_consume, get_nice_gifts


settings = Settings()


def get_nice_digging_block(
    region: Region,
    block: MstEventDiggingBlock,
    raw_consumes: list[MstCommonConsume],
) -> NiceEventDiggingBlock:
    return NiceEventDiggingBlock(
        id=block.id,
        eventId=block.eventId,
        image=fmt_url(
            AssetURL.eventUi,
            base_url=settings.asset_url,
            region=region,
            event=f"Prefabs/{block.eventId}/event_digging_block_{block.imageId}",
        ),
        consumes=[
            get_nice_common_consume(consume)
            for consume in raw_consumes
            if consume.id == block.commonConsumeId
        ],
        objectId=block.objectId,
        diggingEventPoint=block.diggingEventPoint,
        blockNum=block.script["blockNum"],
    )


def get_nice_digging_reward(
    region: Region,
    reward: MstEventDiggingReward,
    gift_data: GiftData,
) -> NiceEventDiggingReward:
    return NiceEventDiggingReward(
        id=reward.id,
        gifts=get_nice_gifts(region, reward.giftId, gift_data),
        rewardSize=reward.rewardSize,
    )


def get_nice_digging(
    region: Region,
    digging: MstEventDigging,
    blocks: list[MstEventDiggingBlock],
    rewards: list[MstEventDiggingReward],
    item_map: dict[int, NiceItem],
    gift_data: GiftData,
    raw_consumes: list[MstCommonConsume],
) -> NiceEventDigging:
    return NiceEventDigging(
        sizeX=digging.sizeX,
        sizeY=digging.sizeY,
        bgImage=fmt_url(
            AssetURL.eventUi,
            base_url=settings.asset_url,
            region=region,
            event=f"Prefabs/{digging.eventId}/digging_bg_{digging.bgImageId}",
        ),
        eventPointItem=item_map[digging.eventPointItemId],
        resettableDiggedNum=digging.resettableDiggedNum,
        blocks=[
            get_nice_digging_block(region, block, raw_consumes)
            for block in blocks
            if block.eventId == digging.eventId
        ],
        rewards=[
            get_nice_digging_reward(region, reward, gift_data)
            for reward in rewards
            if reward.eventId == digging.eventId
        ],
    )
