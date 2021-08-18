from collections import defaultdict

from pydantic import DirectoryPath

from ..schemas.enums import FUNC_VALS_NOT_BUFF
from ..schemas.raw import (
    MstCommandCodeSkill,
    MstEquipSkill,
    MstFunc,
    MstSkill,
    MstSkillLv,
    MstSvt,
    MstSvtAppendPassiveSkill,
    MstSvtPassiveSkill,
    MstSvtSkill,
    MstSvtTreasureDevice,
    MstTreasureDevice,
    MstTreasureDeviceLv,
)
from .utils import load_master_data


def get_buff_to_func(gamedata_path: DirectoryPath) -> dict[int, list[int]]:
    mstFuncs = load_master_data(gamedata_path, MstFunc)

    buff_to_func: dict[int, set[int]] = defaultdict(set)
    for func in mstFuncs:
        if func.funcType not in FUNC_VALS_NOT_BUFF:
            for buff_id in func.vals:
                buff_to_func[buff_id].add(func.id)

    return {buff_id: sorted(func_ids) for buff_id, func_ids in buff_to_func.items()}


def get_func_to_skill(gamedata_path: DirectoryPath) -> dict[int, list[int]]:
    mstSkillLvs = load_master_data(gamedata_path, MstSkillLv)
    mstSkills = load_master_data(gamedata_path, MstSkill)
    skill_ids = {mstSkill.id for mstSkill in mstSkills}

    func_to_skill: dict[int, set[int]] = defaultdict(set)
    for skill_lv in mstSkillLvs:
        if skill_lv.skillId in skill_ids:
            for func_id in skill_lv.funcId:
                func_to_skill[func_id].add(skill_lv.skillId)

    return {func_id: sorted(skill_ids) for func_id, skill_ids in func_to_skill.items()}


def get_func_to_td(gamedata_path: DirectoryPath) -> dict[int, list[int]]:
    mstTdLvs = load_master_data(gamedata_path, MstTreasureDeviceLv)
    mstTds = load_master_data(gamedata_path, MstTreasureDevice)
    td_ids = {mstTd.id for mstTd in mstTds}

    func_to_td: dict[int, set[int]] = defaultdict(set)
    for td_lv in mstTdLvs:
        if td_lv.treaureDeviceId in td_ids:
            for func_id in td_lv.funcId:
                func_to_td[func_id].add(td_lv.treaureDeviceId)

    return {func_id: sorted(td_ids) for func_id, td_ids in func_to_td.items()}


def get_td_to_svt(gamedata_path: DirectoryPath) -> dict[int, list[int]]:
    mstSvtTds = load_master_data(gamedata_path, MstSvtTreasureDevice)

    td_to_svt = defaultdict(set)
    for svt_skill in mstSvtTds:
        td_to_svt[svt_skill.treasureDeviceId].add(svt_skill.svtId)

    return {td_id: sorted(svt_ids) for td_id, svt_ids in td_to_svt.items()}


def get_active_skill_to_svt(gamedata_path: DirectoryPath) -> dict[int, list[int]]:
    mstSvtSkills = load_master_data(gamedata_path, MstSvtSkill)

    active_skill_to_svt = defaultdict(set)
    for svt_skill in mstSvtSkills:
        active_skill_to_svt[svt_skill.skillId].add(svt_skill.svtId)

    return {
        skill_id: sorted(svt_ids) for skill_id, svt_ids in active_skill_to_svt.items()
    }


def get_passive_skill_to_svt(gamedata_path: DirectoryPath) -> dict[int, list[int]]:
    mstSvts = load_master_data(gamedata_path, MstSvt)
    mstSvtPassives = load_master_data(gamedata_path, MstSvtPassiveSkill)

    passive_skill_to_svt = defaultdict(set)
    for svt in mstSvts:
        for skill_id in svt.classPassive:
            passive_skill_to_svt[skill_id].add(svt.id)
    for svt_passive in mstSvtPassives:
        passive_skill_to_svt[svt_passive.skillId].add(svt_passive.svtId)

    if (gamedata_path / "master" / "mstSvtAppendPassiveSkill.json").exists():
        append_skills = load_master_data(gamedata_path, MstSvtAppendPassiveSkill)
        for append_skill in append_skills:
            passive_skill_to_svt[append_skill.skillId].add(append_skill.svtId)

    return {
        skill_id: sorted(svt_ids) for skill_id, svt_ids in passive_skill_to_svt.items()
    }


def get_skill_to_MC(gamedata_path: DirectoryPath) -> dict[int, list[int]]:
    mstEquipSkills = load_master_data(gamedata_path, MstEquipSkill)

    skill_to_mc: dict[int, set[int]] = defaultdict(set)
    for equip_skill in mstEquipSkills:
        skill_to_mc[equip_skill.skillId].add(equip_skill.equipId)

    return {skill_id: sorted(mc_ids) for skill_id, mc_ids in skill_to_mc.items()}


def get_skill_to_CC(gamedata_path: DirectoryPath) -> dict[int, list[int]]:
    mstCCSkills = load_master_data(gamedata_path, MstCommandCodeSkill)

    skill_to_cc: dict[int, set[int]] = defaultdict(set)
    for cc_skill in mstCCSkills:
        skill_to_cc[cc_skill.skillId].add(cc_skill.commandCodeId)

    return {skill_id: sorted(cc_ids) for skill_id, cc_ids in skill_to_cc.items()}
