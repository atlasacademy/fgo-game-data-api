from ..data.gamedata import masters
from ..schemas.common import Region
from ..schemas.enums import AiType


def buff_to_func(region: Region, buff_id: int) -> set[int]:
    """Returns a set of function ID that uses the given buff ID in vals"""
    return masters[region].buffToFunc.get(buff_id, set())


def func_to_skillId(region: Region, func_id: int) -> set[int]:
    """Returns a set of skill ID that uses the given function ID"""
    return set(sorted(masters[region].funcToSkill.get(func_id, set())))


def func_to_tdId(region: Region, func_id: int) -> set[int]:
    """Returns a set of treasure device (NP) ID that uses the given function ID"""
    return masters[region].funcToTd.get(func_id, set())


def active_to_svtId(region: Region, skill_id: int) -> set[int]:
    """Returns a set of svt ID that has the given skill ID as passive"""
    return masters[region].activeSkillToSvt.get(skill_id, set())


def passive_to_svtId(region: Region, skill_id: int) -> set[int]:
    """Returns a set of svt ID that has the given skill ID as passive"""
    class_passives = masters[region].passiveSkillToSvt.get(skill_id, set())
    extra_massives = masters[region].extraPassiveSkillToSvt.get(skill_id, set())
    return class_passives | extra_massives


def skill_to_MCId(region: Region, skill_id: int) -> set[int]:
    """Returns a set of Mystic Code ID that has the given skill ID"""
    return {
        equip_skill.equipId
        for equip_skill in masters[region].mstEquipSkill
        if equip_skill.skillId == skill_id
    }


def skill_to_CCId(region: Region, skill_id: int) -> set[int]:
    """Returns a set of Command Code ID that has the given skill ID"""
    return {
        cc_skill.commandCodeId
        for cc_skill in masters[region].mstCommandCodeSkill
        if cc_skill.skillId == skill_id
    }


def get_parent_ais(
    region: Region, ai_id: int, field: bool = False
) -> dict[AiType, list[int]]:
    if field:
        return {
            AiType.svt: [],
            AiType.field: sorted(masters[region].parentAiField.get(ai_id, [])),
        }
    else:
        return {
            AiType.svt: sorted(masters[region].parentAiSvt.get(ai_id, [])),
            AiType.field: [],
        }


def get_ai_id_from_skill(region: Region, skill_id: int) -> dict[AiType, list[int]]:
    return {
        AiType.svt: sorted(
            set(
                ai_id
                for ai_act_id in masters[region].skillToAiAct.get(skill_id, [])
                for ai_id in masters[region].aiActToAiSvt.get(ai_act_id, [])
            )
        ),
        AiType.field: sorted(
            set(
                ai_id
                for ai_act_id in masters[region].skillToAiAct.get(skill_id, [])
                for ai_id in masters[region].aiActToAiField.get(ai_act_id, [])
            )
        ),
    }
