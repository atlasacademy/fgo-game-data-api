from ....schemas.gameenums import COMMAND_CARD_ATK_TYPE_NAME
from ....schemas.nice import NiceCardDetail
from ....schemas.raw import MstSvtCard
from ...utils import get_traits_list


def get_nice_card(raw_card: MstSvtCard) -> NiceCardDetail:
    return NiceCardDetail(
        hitsDistribution=raw_card.normalDamage,
        attackIndividuality=get_traits_list(raw_card.attackIndividuality),
        attackType=COMMAND_CARD_ATK_TYPE_NAME[raw_card.attackType],
    )
