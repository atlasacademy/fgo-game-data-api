from typing import Any, Dict, Optional


from ..config import Settings
from .common import Region
from .enums import CLASS_NAME, SVT_TYPE_NAME, SvtType
from .gamedata import masters
from .schemas.nice import ASSET_URL, Language
from .translations import SVT_NAME_JP_EN


settings = Settings()


def get_basic_svt(
    region: Region, item_id: int, lang: Optional[Language] = None
) -> Dict[str, Any]:
    mstSvt = masters[region].mstSvtId[item_id]
    basic_servant = {
        "id": item_id,
        "collectionNo": mstSvt.collectionNo,
        "type": SVT_TYPE_NAME[mstSvt.type],
        "name": mstSvt.name,
        "className": CLASS_NAME[mstSvt.classId],
        "rarity": masters[region].mstSvtLimitId[item_id][0].rarity,
    }

    if mstSvt.type in {SvtType.ENEMY_COLLECTION_DETAIL, SvtType.SERVANT_EQUIP}:
        basic_servant["face"] = ASSET_URL["face"].format(
            base_url=settings.asset_url, region=region, item_id=item_id, i=0
        )
    elif mstSvt.type in {SvtType.NORMAL, SvtType.HEROINE}:
        basic_servant["face"] = ASSET_URL["face"].format(
            base_url=settings.asset_url, region=region, item_id=item_id, i=3
        )

    if region == Region.JP and lang == Language.en:
        basic_servant["name"] = SVT_NAME_JP_EN.get(
            basic_servant["name"], basic_servant["name"]
        )

    return basic_servant
