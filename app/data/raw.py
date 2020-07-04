from typing import Set

from .common import Region
from .enums import FuncType
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
    return {
        item.id
        for item in masters[region].mstFunc
        if buff_id in item.vals and item.id in masters[region].mstFuncId
    }


def func_to_skillId(region: Region, func_id: int) -> Set[int]:
    return {
        item.skillId
        for item in masters[region].mstSkillLv
        if func_id in item.funcId and item.skillId in masters[region].mstSkillId
    }


def func_to_tdId(region: Region, func_id: int) -> Set[int]:
    return {
        item.treaureDeviceId
        for item in masters[region].mstTreasureDeviceLv
        if func_id in item.funcId
        and item.treaureDeviceId in masters[region].mstTreasureDeviceId
    }


def get_buff_entity_no_reverse(region: Region, buff_id: int) -> BuffEntityNoReverse:
    buff_entity = BuffEntityNoReverse(mstBuff=masters[region].mstBuffId[buff_id])
    return buff_entity


def get_buff_entity(region: Region, buff_id: int, reverse: bool = False) -> BuffEntity:
    buff_entity = BuffEntity.parse_obj(get_buff_entity_no_reverse(region, buff_id))
    if reverse:
        buff_entity.reverseFunctions = [
            get_func_entity(region, item_id, reverse)
            for item_id in buff_to_func(region, buff_id)
        ]
    return buff_entity


def get_func_entity_no_reverse(
    region: Region, func_id: int, expand: bool = False
) -> FunctionEntityNoReverse:
    func_entity = FunctionEntityNoReverse(mstFunc=masters[region].mstFuncId[func_id])
    if expand and func_entity.mstFunc.funcType not in {
        FuncType.SUB_STATE,
        FuncType.EVENT_DROP_UP,
        FuncType.GAIN_NP_BUFF_INDIVIDUAL_SUM,
    }:
        func_entity.mstFunc.expandedVals = [
            get_buff_entity_no_reverse(region, buff_id)
            for buff_id in func_entity.mstFunc.vals
            if buff_id in masters[region].mstBuffId
        ]
    return func_entity


def get_func_entity(
    region: Region, func_id: int, reverse: bool = False, expand: bool = False
) -> FunctionEntity:
    func_entity = FunctionEntity.parse_obj(
        get_func_entity_no_reverse(region, func_id, expand)
    )
    if reverse:
        func_entity.reverseSkills = [
            get_skill_entity(region, item_id, reverse)
            for item_id in func_to_skillId(region, func_id)
        ]
        func_entity.reverseTds = [
            get_td_entity(region, item_id, reverse)
            for item_id in func_to_tdId(region, func_id)
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
            skillLv.expandedFuncId = [
                get_func_entity_no_reverse(region, func_id, expand)
                for func_id in skillLv.funcId
                if func_id in masters[region].mstFuncId
            ]
    return skill_entity


def get_skill_entity(
    region: Region, skill_id: int, reverse: bool = False, expand: bool = False
) -> SkillEntity:
    skill_entity = SkillEntity.parse_obj(
        get_skill_entity_no_reverse(region, skill_id, expand)
    )

    if reverse:
        activeSkills = {item.svtId for item in skill_entity.mstSvtSkill}
        passiveSkills = {
            item.id for item in masters[region].mstSvt if skill_id in item.classPassive
        }
        skill_entity.reverseServants = [
            get_servant_entity(region, item) for item in activeSkills | passiveSkills
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
            tdLv.expandedFuncId = [
                get_func_entity_no_reverse(region, func_id, expand)
                for func_id in tdLv.funcId
                if func_id in masters[region].mstFuncId
            ]
    return td_entity


def get_td_entity(
    region: Region, td_id: int, reverse: bool = False, expand: bool = False
) -> TdEntity:
    td_entity = TdEntity.parse_obj(get_td_entity_no_reverse(region, td_id, expand))

    if reverse:
        td_entity.reverseServants = [
            get_servant_entity(region, item.svtId)
            for item in td_entity.mstSvtTreasureDevice
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
        svt_entity.mstSvt.expandedClassPassive = [
            get_skill_entity_no_reverse(region, passiveSkill, expand)
            for passiveSkill in svt_entity.mstSvt.classPassive
            if passiveSkill in masters[region].mstSkillId
        ]

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
