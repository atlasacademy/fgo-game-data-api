from typing import Set

from .common import Region
from .gamedata import masters
from .schemas.raw import (
    BuffEntity,
    BuffEntityNoReverse,
    FunctionEntity,
    FunctionEntityNoReverse,
    MysticCodeEntity,
    QuestPhaseEntity,
    ServantEntity,
    SkillEntity,
    SkillEntityNoReverse,
    TdEntity,
    TdEntityNoReverse,
)


def buff_to_func(region: Region, buff_id: int) -> Set[int]:
    return {item.id for item in masters[region].mstFunc if buff_id in item.vals}


def func_to_skillId(region: Region, func_id: int) -> Set[int]:
    return {
        item.skillId for item in masters[region].mstSkillLv if func_id in item.funcId
    }


def func_to_tdId(region: Region, func_id: int) -> Set[int]:
    return {
        item.treaureDeviceId
        for item in masters[region].mstTreasureDeviceLv
        if func_id in item.funcId
    }


def get_buff_entity_no_reverse(region: Region, buff_id: int) -> BuffEntityNoReverse:
    buff_entity = BuffEntityNoReverse(mstBuff=masters[region].mstBuffId[buff_id])
    return buff_entity


def get_buff_entity(region: Region, buff_id: int, reverse: bool = False) -> BuffEntity:
    buff_entity = BuffEntity.parse_obj(get_buff_entity_no_reverse(region, buff_id))
    if reverse:
        reverseFunctions = buff_to_func(region, buff_id)
        buff_entity.reverseFunctions = [
            get_func_entity(region, item_id, reverse) for item_id in reverseFunctions
        ]
    return buff_entity


def get_func_entity_no_reverse(
    region: Region, func_id: int, expand: bool = False
) -> FunctionEntityNoReverse:
    func_entity = FunctionEntityNoReverse(mstFunc=masters[region].mstFuncId[func_id])
    if expand:
        expandedBuff = []
        for buff_id in func_entity.mstFunc.vals:
            if buff_id in masters[region].mstBuffId:
                expandedBuff.append(get_buff_entity_no_reverse(region, buff_id))
        func_entity.mstFunc.expandedVals = expandedBuff
    return func_entity


def get_func_entity(
    region: Region, func_id: int, reverse: bool = False, expand: bool = False
) -> FunctionEntity:
    func_entity = FunctionEntity.parse_obj(
        get_func_entity_no_reverse(region, func_id, expand)
    )
    if reverse:
        reverseSkillIds = func_to_skillId(region, func_id)
        func_entity.reverseSkills = [
            get_skill_entity(region, item_id, reverse) for item_id in reverseSkillIds
        ]
        reverseTdIds = func_to_tdId(region, func_id)
        func_entity.reverseTds = [
            get_td_entity(region, item_id, reverse) for item_id in reverseTdIds
        ]
    return func_entity


def get_skill_entity_no_reverse(
    region: Region, skill_id: int, expand: bool = False
) -> SkillEntityNoReverse:
    skill_entity = SkillEntityNoReverse(
        mstSkill=masters[region].mstSkillId[skill_id],
        mstSkillDetail=masters[region].mstSkillDetailId.get(skill_id, []),
        mstSvtSkill=masters[region].mstSvtSkillId.get(skill_id, []),
        mstSkillLv=masters[region].mstSkillLvId.get(skill_id, []),
    )

    if expand:
        for skillLv in skill_entity.mstSkillLv:
            expandedFunc = []
            for func_id in skillLv.funcId:
                if func_id in masters[region].mstFuncId:
                    expandedFunc.append(
                        get_func_entity_no_reverse(region, func_id, expand)
                    )
            skillLv.expandedFuncId = expandedFunc
    return skill_entity


def get_skill_entity(
    region: Region, skill_id: int, reverse: bool = False, expand: bool = False
) -> SkillEntity:
    skill_entity = SkillEntity.parse_obj(
        get_skill_entity_no_reverse(region, skill_id, expand)
    )

    if reverse:
        reverseServantIds = {item.svtId for item in skill_entity.mstSvtSkill}
        skill_entity.reverseServants = [
            get_servant_entity(region, item_id) for item_id in reverseServantIds
        ]
    return skill_entity


def get_td_entity_no_reverse(
    region: Region, td_id: int, expand: bool = False
) -> TdEntityNoReverse:
    td_entity = TdEntityNoReverse(
        mstTreasureDevice=masters[region].mstTreasureDeviceId[td_id],
        mstTreasureDeviceDetail=masters[region].mstTreasureDeviceDetailId.get(
            td_id, []
        ),
        mstSvtTreasureDevice=masters[region].mstSvtTreasureDeviceId.get(td_id, []),
        mstTreasureDeviceLv=masters[region].mstTreasureDeviceLvId.get(td_id, []),
    )

    if expand:
        for tdLv in td_entity.mstTreasureDeviceLv:
            expandedFunc = []
            for func_id in tdLv.funcId:
                if func_id in masters[region].mstFuncId:
                    expandedFunc.append(
                        get_func_entity_no_reverse(region, func_id, expand)
                    )
            tdLv.expandedFuncId = expandedFunc
    return td_entity


def get_td_entity(
    region: Region, td_id: int, reverse: bool = False, expand: bool = False
) -> TdEntity:
    td_entity = TdEntity.parse_obj(get_td_entity_no_reverse(region, td_id, expand))

    if reverse:
        reverseServantIds = {item.svtId for item in td_entity.mstSvtTreasureDevice}
        td_entity.reverseServants = [
            get_servant_entity(region, item_id) for item_id in reverseServantIds
        ]
    return td_entity


def get_servant_entity(
    region: Region, servant_id: int, expand: bool = False, lore: bool = False
) -> ServantEntity:
    svt_entity = ServantEntity(
        mstSvt=masters[region].mstSvtId[servant_id],
        mstSvtCard=masters[region].mstSvtCardId.get(servant_id, []),
        mstSvtLimit=masters[region].mstSvtLimitId.get(servant_id, []),
        mstCombineSkill=masters[region].mstCombineSkillId.get(servant_id, []),
        mstCombineLimit=masters[region].mstCombineLimitId.get(servant_id, []),
        mstSvtLimitAdd=masters[region].mstSvtLimitAddId.get(servant_id, []),
        mstSkill=[
            get_skill_entity_no_reverse(region, skill, expand)
            for skill in [
                item.skillId
                for item in masters[region].mstSvtSkill
                if item.svtId == servant_id
            ]
        ],
        mstTreasureDevice=[
            get_td_entity_no_reverse(region, td, expand)
            for td in [
                item.treasureDeviceId
                for item in masters[region].mstSvtTreasureDevice
                if item.svtId == servant_id and item.treasureDeviceId != 100
            ]
        ],
    )

    if expand:
        expandedPassive = []
        for passiveSkill in svt_entity.mstSvt.classPassive:
            if passiveSkill in masters[region].mstSkillId:
                expandedPassive.append(
                    get_skill_entity_no_reverse(region, passiveSkill, expand)
                )
        svt_entity.mstSvt.expandedClassPassive = expandedPassive

    if lore:
        svt_entity.mstSvtComment = masters[region].mstSvtCommentId.get(servant_id, [])

    return svt_entity


def get_mystic_code_entity(
    region: Region, mc_id: int, expand: bool = False
) -> MysticCodeEntity:
    mc_entity = MysticCodeEntity(
        mstEquip=masters[region].mstEquipId[mc_id],
        mstSkill=[
            get_skill_entity_no_reverse(region, skill, expand)
            for skill in [
                mc.skillId
                for mc in masters[region].mstEquipSkill
                if mc.equipId == mc_id
            ]
        ],
        mstEquipExp=[mc for mc in masters[region].mstEquipExp if mc.equipId == mc_id],
    )
    return mc_entity


def get_quest_phase_entity(
    region: Region, quest_id: int, phase: int
) -> QuestPhaseEntity:
    return QuestPhaseEntity(
        mstQuest=masters[region].mstQuestId[quest_id],
        mstQuestPhase=masters[region].mstQuestPhaseId[quest_id][phase],
    )
