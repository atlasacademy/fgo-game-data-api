from ....schemas.gameenums import EVENT_REWARD_SCENE_FLAG
from ....schemas.nice import NiceEventRewardScene, NiceEventRewardSceneGuide
from ....schemas.raw import MstEventRewardScene
from ...utils import get_flags


def get_nice_event_reward_scene(
    reward_scene: MstEventRewardScene,
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

    return NiceEventRewardScene(
        slot=reward_scene.slot,
        groupId=reward_scene.groupId,
        type=reward_scene.type,
        guides=guides,
        tabImageId=reward_scene.tabImageId,
        imageId=reward_scene.imageId,
        bgId=reward_scene.bgId,
        bgmId=reward_scene.bgmId,
        afterBgmId=reward_scene.afterBgmId,
        flags=get_flags(reward_scene.flag, EVENT_REWARD_SCENE_FLAG),
    )
