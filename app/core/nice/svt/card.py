from typing import Any

import orjson

from ....schemas.gameenums import (
    COMMAND_CARD_ATK_TYPE_NAME,
    SVT_CARD_POSITION_DAMAGE_RATES_SLIDE_TYPE_NAME,
)
from ....schemas.nice import NiceCardDetail
from ....schemas.raw import MstSvtCard, MstSvtCardAdd
from ...utils import get_traits_list


def get_nice_card(
    raw_card: MstSvtCard, card_add: MstSvtCardAdd | None
) -> NiceCardDetail:
    script: dict[str, Any] = orjson.loads(card_add.script) if card_add else {}
    return NiceCardDetail(
        hitsDistribution=raw_card.normalDamage,
        attackIndividuality=get_traits_list(raw_card.attackIndividuality),
        attackType=COMMAND_CARD_ATK_TYPE_NAME[raw_card.attackType],
        damageRate=script.get("damageRate"),
        attackNpRate=script.get("attackNpRate"),
        defenseNpRate=script.get("defenseNpRate"),
        dropStarRate=script.get("dropStarRate"),
        positionDamageRates=script.get("positionDamageRates"),
        positionDamageRatesSlideType=(
            SVT_CARD_POSITION_DAMAGE_RATES_SLIDE_TYPE_NAME[
                script["positionDamageRatesSlideType"]
            ]
            if "positionDamageRatesSlideType" in script
            else None
        ),
    )
