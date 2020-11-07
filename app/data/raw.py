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
    QuestEntity,
    QuestPhaseEntity,
    ReversedBuff,
    ReversedBuffType,
    ReversedFunction,
    ReversedFunctionType,
    ReversedSkillTd,
    ReversedSkillTdType,
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


def skill_to_MCId(region: Region, skill_id: int) -> Set[int]:
    return {
        item.equipId
        for item in masters[region].mstEquipSkill
        if item.skillId == skill_id
    }


def skill_to_CCId(region: Region, skill_id: int) -> Set[int]:
    return {
        item.commandCodeId
        for item in masters[region].mstCommandCodeSkill
        if item.skillId == skill_id
    }


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
        buff_reverse = ReversedBuff(
            function=(
                get_func_entity(region, item_id, reverse, reverseDepth)
                for item_id in buff_to_func(region, buff_id)
            )
        )
        buff_entity.reverse = ReversedBuffType(raw=buff_reverse)
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
        func_reverse = ReversedFunction(
            skill=(
                get_skill_entity(region, item_id, reverse, reverseDepth)
                for item_id in func_to_skillId(region, func_id)
            ),
            NP=(
                get_td_entity(region, item_id, reverse, reverseDepth)
                for item_id in func_to_tdId(region, func_id)
            ),
        )
        func_entity.reverse = ReversedFunctionType(raw=func_reverse)
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
        skill_reverse = ReversedSkillTd(
            servant=(
                get_servant_entity(region, item)
                for item in activeSkills | passiveSkills
            ),
            MC=(
                get_mystic_code_entity(region, item)
                for item in skill_to_MCId(region, skill_id)
            ),
            CC=(
                get_command_code_entity(region, item)
                for item in skill_to_CCId(region, skill_id)
            ),
        )
        skill_entity.reverse = ReversedSkillTdType(raw=skill_reverse)
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
        td_reverse = ReversedSkillTd(
            servant=(
                get_servant_entity(region, item.svtId)
                for item in td_entity.mstSvtTreasureDevice
            )
        )
        td_entity.reverse = ReversedSkillTdType(raw=td_reverse)
    return td_entity


def get_servant_entity(
    region: Region, servant_id: int, expand: bool = False, lore: bool = False
) -> ServantEntity:
    mstSvt = masters[region].mstSvtId[servant_id]

    svt_entity = ServantEntity(
        mstSvt=mstSvt,
        mstSvtCard=masters[region].mstSvtCardId.get(servant_id, []),
        mstSvtLimit=masters[region].mstSvtLimitId.get(servant_id, []),
        mstCombineSkill=masters[region].mstCombineSkillId.get(
            mstSvt.combineSkillId, []
        ),
        mstCombineLimit=masters[region].mstCombineLimitId.get(
            mstSvt.combineLimitId, []
        ),
        mstCombineCostume=masters[region].mstCombineCostumeId.get(servant_id, []),
        mstSvtLimitAdd=masters[region].mstSvtLimitAddId.get(servant_id, []),
        mstSvtChange=masters[region].mstSvtChangeId.get(servant_id, []),
        # needed costume to get the nice limits and costume ids
        mstSvtCostume=masters[region].mstSvtCostumeId.get(servant_id, []),
        mstSkill=(
            get_skill_entity_no_reverse(region, skill, expand)
            for skill in masters[region].mstSvtSkillSvtId.get(servant_id, [])
        ),
        mstTreasureDevice=(
            get_td_entity_no_reverse(region, td, expand)
            for td in masters[region].mstSvtTreasureDeviceSvtId.get(servant_id, [])
            if td != 100
        ),
    )

    if expand:
        svt_entity.mstSvt.expandedClassPassive = [
            get_skill_entity_no_reverse(region, passiveSkill, expand)
            for passiveSkill in svt_entity.mstSvt.classPassive
            if passiveSkill in masters[region].mstSkillId
        ]

    if lore:
        svt_entity.mstSvtComment = masters[region].mstSvtCommentId.get(servant_id, [])

        # Try to match order in the voice tab in game
        voices = []
        subtitles = []

        for change in svt_entity.mstSvtChange:
            voices += masters[region].mstSvtVoiceId.get(change.svtVoiceId, [])
            subtitles += masters[region].mstSubtitleId.get(change.svtVoiceId, [])

        voices += masters[region].mstSvtVoiceId.get(servant_id, [])
        subtitles += masters[region].mstSubtitleId.get(servant_id, [])

        for main_id, sub_id in (
            ("JEKYLL_SVT_ID", "HYDE_SVT_ID"),
            ("MASHU_SVT_ID1", "MASHU_SVT_ID2"),
        ):
            if servant_id == masters[region].mstConstantId[main_id]:
                sub_svt_id = masters[region].mstConstantId[sub_id]
                voices += masters[region].mstSvtVoiceId.get(sub_svt_id, [])

        # Moriarty deadheat summer lines use his hidden name svt_id
        for svt_id in [change.svtVoiceId for change in svt_entity.mstSvtChange] + [
            servant_id
        ]:
            if voiceRelations := masters[region].mstSvtVoiceRelationId.get(svt_id):
                for voiceRelation in voiceRelations:
                    relation_id = voiceRelation.relationSvtId
                    voices += masters[region].mstSvtVoiceId.get(relation_id, [])
                    subtitles += masters[region].mstSubtitleId.get(relation_id, [])

        svt_entity.mstSvtVoice = voices
        svt_entity.mstSubtitle = subtitles

    return svt_entity


def get_mystic_code_entity(
    region: Region, mc_id: int, expand: bool = False
) -> MysticCodeEntity:
    mc_entity = MysticCodeEntity(
        mstEquip=masters[region].mstEquipId[mc_id],
        mstSkill=(
            get_skill_entity_no_reverse(region, mc.skillId, expand)
            for mc in masters[region].mstEquipSkill
            if mc.equipId == mc_id
        ),
        mstEquipExp=(mc for mc in masters[region].mstEquipExp if mc.equipId == mc_id),
    )
    return mc_entity


def get_command_code_entity(
    region: Region, cc_id: int, expand: bool = False
) -> CommandCodeEntity:
    cc_entity = CommandCodeEntity(
        mstCommandCode=masters[region].mstCommandCodeId[cc_id],
        mstSkill=(
            get_skill_entity_no_reverse(region, item.skillId, expand)
            for item in masters[region].mstCommandCodeSkill
            if item.commandCodeId == cc_id
        ),
        mstCommandCodeComment=[
            item
            for item in masters[region].mstCommandCodeComment
            if item.commandCodeId == cc_id
        ][0],
    )
    return cc_entity


def get_quest_entity(region: Region, quest_id: int) -> QuestEntity:
    return QuestEntity(
        mstQuest=masters[region].mstQuestId[quest_id],
        mstQuestRelease=masters[region].mstQuestReleaseId.get(quest_id, []),
    )


def get_quest_phase_entity(
    region: Region, quest_id: int, phase: int
) -> QuestPhaseEntity:
    return QuestPhaseEntity(
        mstQuest=masters[region].mstQuestId[quest_id],
        mstQuestRelease=masters[region].mstQuestReleaseId.get(quest_id, []),
        mstQuestPhase=masters[region].mstQuestPhaseId[quest_id][phase],
    )
