from ....schemas.gameenums import (
    COMBINE_ADJUST_TARGET_TYPE_NAME,
    EVENT_COMBINE_CALC_TYPE_NAME,
)
from ....schemas.nice import NiceEventCampaign, NiceEventQuest
from ....schemas.raw import MstEventCampaign, MstEventQuest


def get_nice_campaign(campaign: MstEventCampaign) -> NiceEventCampaign:
    return NiceEventCampaign(
        targetIds=campaign.targetIds,
        warIds=campaign.warIds,
        warGroupIds=campaign.warGroupIds or [],
        target=COMBINE_ADJUST_TARGET_TYPE_NAME[campaign.target],
        idx=campaign.idx,
        value=campaign.value,
        calcType=EVENT_COMBINE_CALC_TYPE_NAME[campaign.calcType],
        entryCondMessage=campaign.entryCondMessage,
    )


def get_nice_event_quest(quest: MstEventQuest) -> NiceEventQuest:
    return NiceEventQuest(questId=quest.questId, phase=quest.phase)
