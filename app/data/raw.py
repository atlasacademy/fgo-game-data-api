from typing import Set

from .common import Region, ReverseDepth
from .enums import FUNC_VALS_NOT_BUFF
from .gamedata import masters
from .schemas.raw import (
    BuffEntity,
    BuffEntityNoReverse,
    CommandCodeEntity,
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
    return masters[region].buffToFunc.get(buff_id, set())


def func_to_skillId(region: Region, func_id: int) -> Set[int]:
    return masters[region].funcToSkill.get(func_id, set())


def func_to_tdId(region: Region, func_id: int) -> Set[int]:
    return masters[region].funcToTd.get(func_id, set())


def passive_to_svtId(region: Region, skill_id: int) -> Set[int]:
    return masters[region].passiveSkillToSvt.get(skill_id, set())


def get_buff_entity_no_reverse(region: Region, buff_id: int) -> BuffEntityNoReverse:
    buff_entity = BuffEntityNoReverse(mstBuff=masters[region].mstBuffId[buff_id])
    return buff_entity


def get_buff_entity(
    region: Region,
    buff_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
) -> BuffEntity:
    buff_entity = BuffEntity.parse_obj(get_buff_entity_no_reverse(region, buff_id))
    if reverse and reverseDepth >= ReverseDepth.function:
        buff_entity.reverseFunctions = [
            get_func_entity(region, item_id, reverse, reverseDepth)
            for item_id in buff_to_func(region, buff_id)
        ]
    return buff_entity


def get_func_entity_no_reverse(
    region: Region, func_id: int, expand: bool = False
) -> FunctionEntityNoReverse:
    func_entity = FunctionEntityNoReverse(mstFunc=masters[region].mstFuncId[func_id])
    if expand and func_entity.mstFunc.funcType not in FUNC_VALS_NOT_BUFF:
        func_entity.mstFunc.expandedVals = [
            get_buff_entity_no_reverse(region, buff_id)
            for buff_id in func_entity.mstFunc.vals
            if buff_id in masters[region].mstBuffId
        ]
    return func_entity


def get_func_entity(
    region: Region,
    func_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
    expand: bool = False,
) -> FunctionEntity:
    func_entity = FunctionEntity.parse_obj(
        get_func_entity_no_reverse(region, func_id, expand)
    )
    if reverse and reverseDepth >= ReverseDepth.skillNp:
        func_entity.reverseSkills = [
            get_skill_entity(region, item_id, reverse, reverseDepth)
            for item_id in func_to_skillId(region, func_id)
        ]
        func_entity.reverseTds = [
            get_td_entity(region, item_id, reverse, reverseDepth)
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
    region: Region,
    skill_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.servant,
    expand: bool = False,
) -> SkillEntity:
    skill_entity = SkillEntity.parse_obj(
        get_skill_entity_no_reverse(region, skill_id, expand)
    )

    if reverse and reverseDepth >= ReverseDepth.servant:
        activeSkills = {item.svtId for item in skill_entity.mstSvtSkill}
        passiveSkills = passive_to_svtId(region, skill_id)
        skill_entity.reverseServants = [
            get_servant_entity(region, item) for item in activeSkills | passiveSkills
        ]
        skill_entity.reverseMC = [
            get_mystic_code_entity(region, item.equipId)
            for item in masters[region].mstEquipSkill
            if item.skillId == skill_id
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
    region: Region,
    td_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.servant,
    expand: bool = False,
) -> TdEntity:
    td_entity = TdEntity.parse_obj(get_td_entity_no_reverse(region, td_id, expand))

    if reverse and reverseDepth >= ReverseDepth.servant:
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
            for skill in masters[region].mstSvtSkillSvtId.get(servant_id, [])
        ],
        mstTreasureDevice=[
            get_td_entity_no_reverse(region, td, expand)
            for td in masters[region].mstSvtTreasureDeviceSvtId.get(servant_id, [])
            if td != 100
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


def get_command_code_entity(
    region: Region, cc_id: int, expand: bool = False
) -> CommandCodeEntity:
    cc_entity = CommandCodeEntity(
        mstCommandCode=masters[region].mstCommandCodeId[cc_id],
        mstSkill=[
            get_skill_entity_no_reverse(region, skill, expand)
            for skill in [
                item.skillId
                for item in masters[region].mstCommandCodeSkill
                if item.commandCodeId == cc_id
            ]
        ],
        mstCommandCodeComment=[
            item
            for item in masters[region].mstCommandCodeComment
            if item.commandCodeId == cc_id
        ][0],
    )
    return cc_entity


def get_quest_phase_entity(
    region: Region, quest_id: int, phase: int
) -> QuestPhaseEntity:
    return QuestPhaseEntity(
        mstQuest=masters[region].mstQuestId[quest_id],
        mstQuestPhase=masters[region].mstQuestPhaseId[quest_id][phase],
    )
