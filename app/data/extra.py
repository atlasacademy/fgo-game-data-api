from collections import defaultdict

from pydantic import DirectoryPath

from ..core.nice.base_script import get_script_url
from ..schemas.common import NiceCostume, NiceValentineScript, Region
from ..schemas.gameenums import CondType, PurchaseType, SvtType
from ..schemas.raw import (
    MstEvent,
    MstShop,
    MstShopRelease,
    MstShopScript,
    MstSkill,
    MstSvt,
    MstSvtComment,
    MstSvtCostume,
    MstSvtExtra,
    MstSvtLimitAdd,
    MstSvtSkill,
)
from .utils import load_master_data


VALENTINE_NAME = {
    Region.NA: "Valentine",
    Region.JP: "バレンタイン",
    Region.CN: "情人节",
    Region.KR: "발렌타인",
    Region.TW: "情人節",
}
MASHU_SVT_ID1 = 800100
MASH_NAME = {
    Region.NA: "Mash",
    Region.JP: "マシュ",
    Region.CN: "玛修",
    Region.KR: "마슈",
    Region.TW: "瑪修",
}


def is_Mash_Valentine_equip(region: Region, comment: str) -> bool:
    header = comment.split("\n")[0]
    return VALENTINE_NAME[region] in header and MASH_NAME[region] in header


def get_extra_svt_data(
    region: Region, gamedata_path: DirectoryPath
) -> list[MstSvtExtra]:
    mstSvts = load_master_data(gamedata_path, MstSvt)
    mstSvtLimitAdds = load_master_data(gamedata_path, MstSvtLimitAdd)
    mstSkills = load_master_data(gamedata_path, MstSkill)
    mstSvtSkills = load_master_data(gamedata_path, MstSvtSkill)
    mstEvents = load_master_data(gamedata_path, MstEvent)
    mstShops = load_master_data(gamedata_path, MstShop)
    mstShopScripts = load_master_data(gamedata_path, MstShopScript)
    mstShopReleases = load_master_data(gamedata_path, MstShopRelease)
    mstSvtComments = load_master_data(gamedata_path, MstSvtComment)
    mstSvtCostumes = load_master_data(gamedata_path, MstSvtCostume)

    mstSkillId = {mstSkill.id: mstSkill for mstSkill in mstSkills}
    mstSvtId = {mstSvt.id: mstSvt for mstSvt in mstSvts}

    mstSvtSkillSvtId: dict[int, list[MstSvtSkill]] = defaultdict(list)
    for svtSkill in mstSvtSkills:
        mstSvtSkillSvtId[svtSkill.svtId].append(svtSkill)

    mstShopReleaseShopId: dict[int, list[MstShopRelease]] = defaultdict(list)
    for shop_release in mstShopReleases:
        mstShopReleaseShopId[shop_release.shopId].append(shop_release)

    mstSvtCostumeId: dict[int, dict[int, MstSvtCostume]] = defaultdict(dict)
    for costume in mstSvtCostumes:
        mstSvtCostumeId[costume.svtId][costume.id] = costume

    # Bond CE has servant's ID in skill's actIndividuality
    # to bind the CE effect to the servant
    bondEquip: dict[int, int] = {}
    for mstSvt in mstSvts:
        if mstSvt.type == SvtType.SERVANT_EQUIP and mstSvt.id in mstSvtSkillSvtId:
            actIndividualities = set()
            for svtSkill in mstSvtSkillSvtId[mstSvt.id]:
                mstSkill = mstSkillId.get(svtSkill.skillId)
                if mstSkill:
                    actIndividualities.add(tuple(mstSkill.actIndividuality))
            if len(actIndividualities) == 1:
                individualities = actIndividualities.pop()
                for individuality in individualities:
                    if individuality in mstSvtId:
                        bondEquip[individuality] = mstSvt.id

    bondEquipOwner = {
        equip_id: svt_id
        for svt_id, equip_id in bondEquip.items()
        if mstSvtId[svt_id].collectionNo != 0
    }

    valentineEquip: dict[int, list[int]] = defaultdict(list)
    valentineScript: dict[int, list[NiceValentineScript]] = defaultdict(list)

    mstShopScriptId = {script.shopId: script for script in mstShopScripts}
    eventId_with_script = {
        shop.eventId for shop in mstShops if shop.id in mstShopScriptId
    }

    latest_valentine_event_id = max(
        (event for event in mstEvents if event.id in eventId_with_script),
        key=lambda event: int(event.startedAt),
    ).id

    # Find Valentince CE's owner by looking at which servant unlock the shop entries
    for shop in mstShops:
        if (
            shop.eventId == latest_valentine_event_id
            and shop.purchaseType == PurchaseType.SERVANT
        ):
            for shop_release in mstShopReleaseShopId[shop.id]:
                if shop_release.condType == CondType.SVT_GET:
                    svt_id = shop_release.condValues[0]
                    equip_id = shop.targetIds[0]

                    valentineEquip[svt_id].append(equip_id)

                    shop_script = mstShopScriptId[shop.id]
                    nice_val_script = NiceValentineScript(
                        scriptName=shop_script.name,
                        scriptId=shop_script.scriptId,
                        script=get_script_url(region, shop_script.scriptId),
                    )
                    valentineScript[svt_id].append(nice_val_script)
                    valentineScript[equip_id].append(nice_val_script)
                    break

    valentineEquip[MASHU_SVT_ID1] = [
        item.svtId
        for item in mstSvtComments
        if is_Mash_Valentine_equip(region, item.comment)
    ]
    valentineEquipOwner = {
        equip_id: svt_id
        for svt_id, equip_ids in valentineEquip.items()
        for equip_id in equip_ids
    }

    zeroLimitOverwriteName: dict[int, str] = {}
    svtCostumeIds: dict[int, dict[int, NiceCostume]] = defaultdict(dict)
    for limitAdd in mstSvtLimitAdds:
        if limitAdd.limitCount == 0 and "overWriteServantName" in limitAdd.script:
            zeroLimitOverwriteName[limitAdd.svtId] = limitAdd.script[
                "overWriteServantName"
            ]
        if limitAdd.limitCount in mstSvtCostumeId.get(limitAdd.svtId, {}):
            raw_costume = mstSvtCostumeId[limitAdd.svtId][limitAdd.limitCount]
            svtCostumeIds[limitAdd.svtId][limitAdd.limitCount] = NiceCostume(
                id=raw_costume.id,
                costumeCollectionNo=raw_costume.costumeCollectionNo,
                battleCharaId=limitAdd.battleCharaId,
                name=raw_costume.name,
                shortName=raw_costume.shortName,
                detail=raw_costume.detail,
                priority=raw_costume.priority,
            )
        else:
            svtCostumeIds[limitAdd.svtId][limitAdd.limitCount] = NiceCostume(
                id=limitAdd.limitCount,
                costumeCollectionNo=0,
                battleCharaId=limitAdd.battleCharaId,
                name="",
                shortName="",
                detail="",
                priority=limitAdd.limitCount,
            )

    all_svt_ids = (
        bondEquip.keys()
        | bondEquipOwner.keys()
        | valentineEquip.keys()
        | valentineScript.keys()
        | valentineEquipOwner.keys()
        | zeroLimitOverwriteName.keys()
        | svtCostumeIds.keys()
    )

    return [
        MstSvtExtra(
            svtId=svt_id,
            zeroLimitOverwriteName=zeroLimitOverwriteName.get(svt_id),
            bondEquip=bondEquip.get(svt_id, 0),
            bondEquipOwner=bondEquipOwner.get(svt_id),
            valentineEquip=valentineEquip.get(svt_id, []),
            valentineScript=valentineScript.get(svt_id, []),
            valentineEquipOwner=valentineEquipOwner.get(svt_id),
            costumeLimitSvtIdMap=svtCostumeIds.get(svt_id, {}),
        )
        for svt_id in sorted(all_svt_ids)
    ]
