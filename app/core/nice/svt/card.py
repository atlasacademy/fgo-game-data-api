from ....schemas.nice import NiceCardDetail
from ....schemas.raw import MstSvtCard
from ...utils import get_traits_list


def get_nice_card(raw_card: MstSvtCard) -> NiceCardDetail:
    return NiceCardDetail(
        attackIndividuality=get_traits_list(raw_card.attackIndividuality)
    )
