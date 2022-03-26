from ....config import Settings
from ....schemas.common import Region
from ....schemas.gameenums import EVENT_REWARD_SCENE_FLAG
from ....schemas.nice import (
    AssetURL,
    NiceBgmEntity,
    NiceEventRewardScene,
    NiceEventRewardSceneGuide,
)
from ....schemas.raw import MstEventRewardScene
from ...utils import fmt_url, get_flags


settings = Settings()


def get_nice_event_reward_scene(
    region: Region,
    reward_scene: MstEventRewardScene,
    nice_bgms: dict[int, NiceBgmEntity],
) -> NiceEventRewardScene:
    guides = [
        NiceEventRewardSceneGuide(
            imageId=guideImageId,
            limitCount=reward_scene.guideLimitCounts[i],
            faceId=reward_scene.guideFaceIds[i]
            if len(reward_scene.guideFaceIds) > i
            else None,
            displayName=reward_scene.guideDisplayNames[i]
            if len(reward_scene.guideDisplayNames) > i
            else None,
            weight=reward_scene.guideWeights[i]
            if len(reward_scene.guideWeights) > i
            else None,
            unselectedMax=reward_scene.guideUnselectedMax[i]
            if len(reward_scene.guideUnselectedMax) > i
            else None,
        )
        for i, guideImageId in enumerate(reward_scene.guideImageIds)
    ]

    event_id = reward_scene.eventId
    base_settings = {"base_url": settings.asset_url, "region": region}

    return NiceEventRewardScene(
        slot=reward_scene.slot,
        groupId=reward_scene.groupId,
        type=reward_scene.type,
        guides=guides,
        tabOnImage=fmt_url(
            AssetURL.eventReward,
            **base_settings,
            fname=f"btn_txt_on_{event_id}_{reward_scene.tabImageId}",
        ),
        tabOffImage=fmt_url(
            AssetURL.eventReward,
            **base_settings,
            fname=f"btn_txt_off_{event_id}_{reward_scene.tabImageId}",
        ),
        image=fmt_url(
            AssetURL.eventReward,
            **base_settings,
            fname=f"event_type_txt_{event_id}_{reward_scene.imageId}",
        )
        if reward_scene.imageId > 0
        else None,
        bg=fmt_url(
            AssetURL.back,
            **base_settings,
            bg_id=reward_scene.bgId,
        ),
        bgm=nice_bgms[reward_scene.bgmId],
        afterBgm=nice_bgms[reward_scene.afterBgmId],
        flags=get_flags(reward_scene.flag, EVENT_REWARD_SCENE_FLAG),
    )
