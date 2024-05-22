from ....schemas.gameenums import COND_TYPE_NAME
from ....schemas.nice import NiceServantTrait
from ....schemas.raw import MstSvtIndividuality
from ...utils import get_traits_list


def get_nice_svt_trait(svt_individuality: MstSvtIndividuality) -> NiceServantTrait:
    return NiceServantTrait(
        idx=svt_individuality.idx,
        trait=get_traits_list(sorted(svt_individuality.individuality)),
        limitCount=svt_individuality.limitCount,
        condType=(
            COND_TYPE_NAME[svt_individuality.condType]
            if svt_individuality.condType is not None
            else None
        ),
        condId=svt_individuality.condId,
        condNum=svt_individuality.condNum,
        eventId=svt_individuality.eventId,
        startedAt=svt_individuality.startedAt,
        endedAt=svt_individuality.endedAt,
    )
