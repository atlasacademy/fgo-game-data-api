from ....config import Settings
from ....schemas.common import Region
from ....schemas.nice import AssetURL, NiceEventTower, NiceEventTowerReward
from ....schemas.raw import MstEventTower, MstEventTowerReward, MstGift
from ...utils import fmt_url
from .utils import get_nice_gifts


settings = Settings()


def get_nice_tower_rewards(
    region: Region, reward: MstEventTowerReward, gift_maps: dict[int, list[MstGift]]
) -> NiceEventTowerReward:
    base_settings = {"base_url": settings.asset_url, "region": region}
    return NiceEventTowerReward(
        floor=reward.floor,
        gifts=get_nice_gifts(reward.giftId, gift_maps),
        boardMessage=reward.boardMessage,
        rewardGet=fmt_url(
            AssetURL.eventReward,
            **base_settings,
            fname=f"event_tower_rewardget_{reward.boardImageId}",
        ),
        banner=fmt_url(
            AssetURL.eventReward,
            **base_settings,
            fname=f"event_towerbanner_{reward.boardImageId}",
        ),
    )


def get_nice_event_tower(
    region: Region,
    tower: MstEventTower,
    rewards: list[MstEventTowerReward],
    gift_maps: dict[int, list[MstGift]],
) -> NiceEventTower:
    return NiceEventTower(
        towerId=tower.towerId,
        name=tower.name,
        rewards=[
            get_nice_tower_rewards(region, reward, gift_maps)
            for reward in rewards
            if reward.towerId == tower.towerId
        ],
    )
