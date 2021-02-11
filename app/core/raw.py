from typing import Iterable, List, Set

from fastapi import HTTPException
from sqlalchemy.engine import Connection

from ..data.gamedata import masters
from ..db.helpers import ai, event, quest, skill, svt, td, war
from ..schemas.common import Region, ReverseDepth
from ..schemas.enums import FUNC_VALS_NOT_BUFF
from ..schemas.raw import (
    AiCollection,
    AiEntity,
    BuffEntity,
    BuffEntityNoReverse,
    CommandCodeEntity,
    EventEntity,
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
    WarEntity,
)


def buff_to_func(region: Region, buff_id: int) -> Set[int]:
    """Returns a set of function ID that uses the given buff ID in vals"""
    return masters[region].buffToFunc.get(buff_id, set())


def func_to_skillId(region: Region, func_id: int) -> Set[int]:
    """Returns a set of skill ID that uses the given function ID"""
    return set(sorted(masters[region].funcToSkill.get(func_id, set())))


def func_to_tdId(region: Region, func_id: int) -> Set[int]:
    """Returns a set of treasure device (NP) ID that uses the given function ID"""
    return masters[region].funcToTd.get(func_id, set())


def active_to_svtId(region: Region, skill_id: int) -> Set[int]:
    """Returns a set of svt ID that has the given skill ID as passive"""
    return masters[region].activeSkillToSvt.get(skill_id, set())


def passive_to_svtId(region: Region, skill_id: int) -> Set[int]:
    """Returns a set of svt ID that has the given skill ID as passive"""
    return masters[region].passiveSkillToSvt.get(skill_id, set())


def skill_to_MCId(region: Region, skill_id: int) -> Set[int]:
    """Returns a set of Mystic Code ID that has the given skill ID"""
    return {
        equip_skill.equipId
        for equip_skill in masters[region].mstEquipSkill
        if equip_skill.skillId == skill_id
    }


def skill_to_CCId(region: Region, skill_id: int) -> Set[int]:
    """Returns a set of Command Code ID that has the given skill ID"""
    return {
        cc_skill.commandCodeId
        for cc_skill in masters[region].mstCommandCodeSkill
        if cc_skill.skillId == skill_id
    }


def get_buff_entity_no_reverse(region: Region, buff_id: int) -> BuffEntityNoReverse:
    buff_entity = BuffEntityNoReverse(mstBuff=masters[region].mstBuffId[buff_id])
    return buff_entity


def get_buff_entity(
    conn: Connection,
    region: Region,
    buff_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
) -> BuffEntity:
    buff_entity = BuffEntity.parse_obj(get_buff_entity_no_reverse(region, buff_id))
    if reverse and reverseDepth >= ReverseDepth.function:
        buff_reverse = ReversedBuff(
            function=(
                get_func_entity(conn, region, func_id, reverse, reverseDepth)
                for func_id in buff_to_func(region, buff_id)
            )
        )
        buff_entity.reverse = ReversedBuffType(raw=buff_reverse)
    return buff_entity


def get_func_entity_no_reverse(
    region: Region, func_id: int, expand: bool = False
) -> FunctionEntityNoReverse:
    func_entity = FunctionEntityNoReverse(
        mstFunc=masters[region].mstFuncId[func_id],
        mstFuncGroup=masters[region].mstFuncGroupId.get(func_id, []),
    )
    if expand and func_entity.mstFunc.funcType not in FUNC_VALS_NOT_BUFF:
        func_entity.mstFunc.expandedVals = [
            get_buff_entity_no_reverse(region, buff_id)
            for buff_id in func_entity.mstFunc.vals
            if buff_id in masters[region].mstBuffId
        ]
    return func_entity


def get_func_entity(
    conn: Connection,
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
                get_skill_entity(conn, region, skill_id, reverse, reverseDepth)
                for skill_id in func_to_skillId(region, func_id)
            ),
            NP=(
                get_td_entity(conn, region, td_id, reverse, reverseDepth)
                for td_id in func_to_tdId(region, func_id)
            ),
        )
        func_entity.reverse = ReversedFunctionType(raw=func_reverse)
    return func_entity


def get_skill_entity_no_reverse_many(
    conn: Connection, region: Region, skill_ids: Iterable[int], expand: bool = False
) -> List[SkillEntityNoReverse]:
    if not skill_ids:
        return []
    skill_entities = skill.get_skillEntity(conn, skill_ids)
    if skill_entities:
        if expand:
            for skill_entity in skill_entities:
                for skillLv in skill_entity.mstSkillLv:
                    skillLv.expandedFuncId = [
                        get_func_entity_no_reverse(region, func_id, expand)
                        for func_id in skillLv.funcId
                        if func_id in masters[region].mstFuncId
                    ]
        return skill_entities
    else:
        raise HTTPException(status_code=404, detail="Skill not found")


def get_skill_entity_no_reverse(
    conn: Connection, region: Region, skill_id: int, expand: bool = False
) -> SkillEntityNoReverse:
    return get_skill_entity_no_reverse_many(conn, region, [skill_id], expand)[0]


def get_skill_entity(
    conn: Connection,
    region: Region,
    skill_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.servant,
    expand: bool = False,
) -> SkillEntity:
    skill_entity = SkillEntity.parse_obj(
        get_skill_entity_no_reverse(conn, region, skill_id, expand)
    )

    if reverse and reverseDepth >= ReverseDepth.servant:
        activeSkills = {svt_skill.svtId for svt_skill in skill_entity.mstSvtSkill}
        passiveSkills = passive_to_svtId(region, skill_id)
        skill_reverse = ReversedSkillTd(
            servant=(
                get_servant_entity(conn, region, svt_id)
                for svt_id in activeSkills | passiveSkills
            ),
            MC=(
                get_mystic_code_entity(conn, region, mc_id)
                for mc_id in skill_to_MCId(region, skill_id)
            ),
            CC=(
                get_command_code_entity(conn, region, cc_id)
                for cc_id in skill_to_CCId(region, skill_id)
            ),
        )
        skill_entity.reverse = ReversedSkillTdType(raw=skill_reverse)
    return skill_entity


def get_td_entity_no_reverse_many(
    conn: Connection, region: Region, td_ids: Iterable[int], expand: bool = False
) -> List[TdEntityNoReverse]:
    if not td_ids:
        return []
    td_entities = td.get_tdEntity(conn, td_ids)
    if td_entities:
        if expand:
            for td_entity in td_entities:
                for tdLv in td_entity.mstTreasureDeviceLv:
                    tdLv.expandedFuncId = [
                        get_func_entity_no_reverse(region, func_id, expand)
                        for func_id in tdLv.funcId
                        if func_id in masters[region].mstFuncId
                    ]
        return td_entities
    else:
        raise HTTPException(status_code=404, detail="NP not found")


def get_td_entity_no_reverse(
    conn: Connection, region: Region, td_id: int, expand: bool = False
) -> TdEntityNoReverse:
    return get_td_entity_no_reverse_many(conn, region, [td_id], expand)[0]


def get_td_entity(
    conn: Connection,
    region: Region,
    td_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.servant,
    expand: bool = False,
) -> TdEntity:
    td_entity = TdEntity.parse_obj(
        get_td_entity_no_reverse(conn, region, td_id, expand)
    )

    if reverse and reverseDepth >= ReverseDepth.servant:
        td_reverse = ReversedSkillTd(
            servant=(
                get_servant_entity(conn, region, svt_id.svtId)
                for svt_id in td_entity.mstSvtTreasureDevice
            )
        )
        td_entity.reverse = ReversedSkillTdType(raw=td_reverse)
    return td_entity


def get_servant_entity(
    conn: Connection,
    region: Region,
    servant_id: int,
    expand: bool = False,
    lore: bool = False,
) -> ServantEntity:
    svt_entity_db = svt.get_servantEntity(conn, servant_id)

    svt_entity = ServantEntity(
        **svt_entity_db,
        # needed this to get CharaFigure available forms
        mstSvtScript=masters[region].mstSvtScriptId.get(servant_id, []),
        mstSkill=(
            get_skill_entity_no_reverse_many(
                conn,
                region,
                [
                    skill.skillId
                    for skill in skill.get_mstSvtSkill(conn, svt_id=servant_id)
                ],
                expand,
            )
        ),
        mstTreasureDevice=(
            get_td_entity_no_reverse_many(
                conn,
                region,
                [
                    td.treasureDeviceId
                    for td in td.get_mstSvtTreasureDevice(conn, svt_id=servant_id)
                    if td.treasureDeviceId != 100
                ],
                expand,
            )
        ),
    )

    if expand:
        svt_entity.mstSvt.expandedClassPassive = get_skill_entity_no_reverse_many(
            conn, region, svt_entity.mstSvt.classPassive, expand
        )

    if lore:
        svt_entity.mstSvtComment = svt.get_mstSvtComment(conn, servant_id)

        # Try to match order in the voice tab in game
        voice_ids = []

        for change in svt_entity.mstSvtChange:
            voice_ids.append(change.svtVoiceId)

        voice_ids.append(servant_id)

        for main_id, sub_id in (
            ("JEKYLL_SVT_ID", "HYDE_SVT_ID"),
            ("MASHU_SVT_ID1", "MASHU_SVT_ID2"),
        ):
            if servant_id == masters[region].mstConstantId[main_id]:
                voice_ids.append(masters[region].mstConstantId[sub_id])

        # Moriarty deadheat summer lines use his hidden name svt_id
        for svt_id in [change.svtVoiceId for change in svt_entity.mstSvtChange] + [
            servant_id
        ]:
            if voiceRelations := masters[region].mstSvtVoiceRelationId.get(svt_id):
                for voiceRelation in voiceRelations:
                    voice_ids.append(voiceRelation.relationSvtId)

        order = {voice_id: i for i, voice_id in enumerate(voice_ids)}
        mstSvtVoice = svt.get_mstSvtVoice(conn, voice_ids)
        mstSubtitle = svt.get_mstSubtitle(conn, voice_ids)

        svt_entity.mstSvtVoice = sorted(mstSvtVoice, key=lambda voice: order[voice.id])
        svt_entity.mstSubtitle = sorted(
            mstSubtitle, key=lambda sub: order[sub.get_svtId()]
        )

    return svt_entity


def get_mystic_code_entity(
    conn: Connection, region: Region, mc_id: int, expand: bool = False
) -> MysticCodeEntity:
    mc_entity = MysticCodeEntity(
        mstEquip=masters[region].mstEquipId[mc_id],
        mstSkill=(
            get_skill_entity_no_reverse_many(
                conn,
                region,
                [
                    mc.skillId
                    for mc in masters[region].mstEquipSkill
                    if mc.equipId == mc_id
                ],
                expand,
            )
        ),
        mstEquipExp=(mc for mc in masters[region].mstEquipExp if mc.equipId == mc_id),
    )
    return mc_entity


def get_command_code_entity(
    conn: Connection, region: Region, cc_id: int, expand: bool = False
) -> CommandCodeEntity:
    cc_entity = CommandCodeEntity(
        mstCommandCode=masters[region].mstCommandCodeId[cc_id],
        mstSkill=(
            get_skill_entity_no_reverse_many(
                conn,
                region,
                [
                    cc_skill.skillId
                    for cc_skill in masters[region].mstCommandCodeSkill
                    if cc_skill.commandCodeId == cc_id
                ],
                expand,
            )
        ),
        mstCommandCodeComment=masters[region].mstCommandCodeCommentId[cc_id][0],
    )
    return cc_entity


def get_war_entity(conn: Connection, region: Region, war_id: int) -> WarEntity:
    return WarEntity(
        mstWar=masters[region].mstWarId[war_id],
        mstMap=masters[region].mstMapWarId.get(war_id, []),
        mstSpot=war.get_mstSpot(conn, war_id),
    )


def get_event_entity(conn: Connection, region: Region, event_id: int) -> EventEntity:
    return EventEntity(
        mstEvent=masters[region].mstEventId[event_id],
        mstShop=event.get_mstShop(conn, event_id),
        mstEventReward=event.get_mstEventReward(conn, event_id),
    )


def get_quest_entity_many(conn: Connection, quest_id: List[int]) -> List[QuestEntity]:
    quest_entities = quest.get_quest_entity(conn, quest_id)
    if quest_entities:
        return quest_entities
    else:
        raise HTTPException(status_code=404, detail="Quest not found")


def get_quest_entity(conn: Connection, quest_id: int) -> QuestEntity:
    return get_quest_entity_many(conn, [quest_id])[0]


def get_quest_entity_by_spot_many(
    conn: Connection, spot_ids: List[int]
) -> List[QuestEntity]:
    return quest.get_quest_by_spot(conn, spot_ids)


def get_quest_phase_entity(
    conn: Connection, quest_id: int, phase: int
) -> QuestPhaseEntity:
    quest_phase = quest.get_quest_phase_entity(conn, quest_id, phase)
    if quest_phase:
        return QuestPhaseEntity.parse_obj(quest_phase)
    else:
        raise HTTPException(status_code=404, detail="Quest phase not found")


def get_ai_entities(
    conn: Connection, ai_id: int, field: bool = False, throw_error: bool = True
) -> List[AiEntity]:
    if field:
        ais = ai.get_field_ai_entity(conn, ai_id)
    else:
        ais = ai.get_svt_ai_entity(conn, ai_id)

    if ais or not throw_error:
        return ais
    else:
        raise HTTPException(status_code=404, detail="AI not found")


def get_ai_collection(
    conn: Connection, ai_id: int, field: bool = False
) -> AiCollection:
    main_ais = get_ai_entities(conn, ai_id, field)
    retreived_ais = {ai_id}

    to_be_retrieved_ais = {
        ai.mstAi.avals[0] for ai in main_ais if ai.mstAi.avals[0] > 0
    }
    related_ais: List[AiEntity] = []
    while to_be_retrieved_ais:
        for related_ai_id in to_be_retrieved_ais:
            related_ais += get_ai_entities(
                conn, related_ai_id, field, throw_error=False
            )

        retreived_ais |= to_be_retrieved_ais
        to_be_retrieved_ais = {
            ai.mstAi.avals[0]
            for ai in related_ais
            if ai.mstAi.avals[0] > 0 and ai.mstAi.avals[0] not in retreived_ais
        }

    return AiCollection(
        mainAis=main_ais,
        relatedAis=related_ais,
    )
