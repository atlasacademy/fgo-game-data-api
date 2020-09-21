import argparse
from typing import Dict, List


def convert_name(name: str) -> str:
    words = name.split("_")
    return "".join([words[0].lower()] + [w.title() for w in words[1:]])


def enum_to_dict(cstype: List[str]) -> Dict[int, str]:
    enum_dict: Dict[int, str] = {}
    for item in cstype:
        item = item.split(";")[0]
        splitted = item.split(" = ")
        i = int(splitted[1])
        item = splitted[0].split()[-1].strip()
        enum_dict[i] = item
    return {k: enum_dict[k] for k in sorted(enum_dict.keys())}


def out_intenum(input_dict: Dict[int, str], className: str) -> List[str]:
    intenum_lines = [f"class {className}(IntEnum):\n"]
    for enumint, enumstr in input_dict.items():
        intenum_lines.append(f"    {enumstr} = {enumint}\n")
    return intenum_lines


EXTRA_STR_NAME = {"NiceStatusRank": ["unknown"]}


STR_NAME_OVERRIDE = {
    "NiceCardType": {"addattack": "extra"},
    "NiceGender": {"other": "unknown"},
    "NiceStatusRank": {
        "a": "A",
        "aPlus": "A+",
        "aPlus2": "A++",
        "aMinus": "A-",
        "aPlus3": "A+++",
        "b": "B",
        "bPlus": "B+",
        "bPlus2": "B++",
        "bMinus": "B-",
        "bPlus3": "B+++",
        "c": "C",
        "cPlus": "C+",
        "cPlus2": "C++",
        "cMinus": "C-",
        "cPlus3": "C+++",
        "d": "D",
        "dPlus": "D+",
        "dPlus2": "D++",
        "dMinus": "D-",
        "dPlus3": "D+++",
        "e": "E",
        "ePlus": "E+",
        "ePlus2": "E++",
        "eMinus": "E-",
        "ePlus3": "E+++",
        "ex": "EX",
        "question": "?",
        "none": "None",
        "unknown": "Unknown",
    },
}


STR_NAME_COMMENT = {
    "NiceBuffLimit": {
        "upper": "  # type: ignore # str has upper and lower methods",
        "lower": "  # type: ignore",
    },
}


def out_strenum(input_dict: Dict[int, str], nice_class: str) -> List[str]:
    strenum_lines = [f"class {nice_class}(str, Enum):\n"]
    for enumstr in list(input_dict.values()) + EXTRA_STR_NAME.get(nice_class, []):
        json_name = convert_name(enumstr)
        str_name = STR_NAME_OVERRIDE.get(nice_class, {}).get(json_name, json_name)
        str_comment = STR_NAME_COMMENT.get(nice_class, {}).get(json_name, "")
        strenum_lines.append(f'    {json_name} = "{str_name}"{str_comment}\n')
    return strenum_lines


def out_enumdict(
    input_dict: Dict[int, str], nice_class: str, dict_name: str
) -> List[str]:
    strenumdict_lines = [f"{dict_name}: Dict[int, {nice_class}] = {{\n"]
    for enumint, enumstr in input_dict.items():
        json_name = convert_name(enumstr)
        strenumdict_lines.append(f"    {enumint}: {nice_class}.{json_name},\n")
    strenumdict_lines.append("}\n")
    return strenumdict_lines


def cs_enums_to_lines(
    cs_enums: List[str], raw_class: str, nice_class: str, dict_name: str
) -> List[str]:
    enum_dict = enum_to_dict(cs_enums)
    if raw_class == "DataValsType":
        return out_intenum(enum_dict, raw_class)
    else:
        return (
            out_intenum(enum_dict, raw_class)
            + ["\n"] * 2
            + out_strenum(enum_dict, nice_class)
            + ["\n"] * 2
            + out_enumdict(enum_dict, nice_class, dict_name)
        )


ENUMS = [
    ("Gender.Type", "GenderType", "NiceGender", "GENDER_TYPE_NAME"),
    ("SvtType.Type", "SvtType", "NiceSvtType", "SVT_TYPE_NAME"),
    ("FuncList.TYPE", "FuncType", "NiceFuncType", "FUNC_TYPE_NAME"),
    ("Target.TYPE", "FuncTargetType", "NiceFuncTargetType", "FUNC_TARGETTYPE_NAME"),
    ("BuffList.TYPE", "BuffType", "NiceBuffType", "BUFF_TYPE_NAME"),
    ("BuffList.ACTION", "BuffAction", "NiceBuffAction", "BUFF_ACTION_NAME"),
    ("BuffList.LIMIT", "BuffLimit", "NiceBuffLimit", "BUFF_LIMIT_NAME"),
    ("DataVals.TYPE", "DataValsType", "NiceDataValsType", "DATA_VALS_TYPE_NAME"),
    (
        "ClassRelationOverwriteEntity",
        "ClassRelationOverwriteType",
        "NiceClassRelationOverwriteType",
        "CLASS_OVERWRITE_NAME",
    ),
    ("ItemType.Type", "ItemType", "NiceItemType", "ITEM_TYPE_NAME"),
    ("BattleCommand.TYPE", "CardType", "NiceCardType", "CARD_TYPE_NAME"),
    ("CondType.Kind", "CondType", "NiceCondType", "COND_TYPE_NAME"),
    ("VoiceCondType.Type", "VoiceCondType", "NiceVoiceCondType", "VOICE_COND_NAME"),
    ("SvtVoiceType.Type", "SvtVoiceType", "NiceSvtVoiceType", "VOICE_TYPE_NAME"),
    ("QuestEntity.enType", "QuestType", "NiceQuestType", "QUEST_TYPE_NAME"),
    (
        "QuestEntity.ConsumeType",
        "QuestConsumeType",
        "NiceConsumeType",
        "QUEST_CONSUME_TYPE_NAME",
    ),
    ("StatusRank.Kind", "StatusRank", "NiceStatusRank", "STATUS_RANK_NAME"),
]


cs_signatures: Dict[str, str] = {f"public enum {enum[0]}": enum[0] for enum in ENUMS}


def main(dump_path: str, gameenums_path: str) -> None:
    print(f"Reading {dump_path} ...")
    with open(dump_path, "r", encoding="utf-8") as fp:
        lines = fp.readlines()

    all_cs_enums: Dict[str, List[str]] = {}
    enum_lines: List[str] = []
    in_recording_signature = ""
    in_recording_mode = False

    for line in lines:
        if not in_recording_mode:
            for signature in cs_signatures:
                if line.startswith(signature):
                    in_recording_signature = cs_signatures[signature]
                    print(f"Found {in_recording_signature}")
                    enum_lines = []
                    in_recording_mode = True
                    continue
        elif line.startswith("}"):
            all_cs_enums[in_recording_signature] = enum_lines
            in_recording_mode = False
            continue
        else:
            if "public const" in line:
                enum_lines.append(line.strip())

    not_found = cs_signatures.values() - all_cs_enums.keys()
    for item in not_found:
        print(f"Can't find {item}")

    python_lines = [
        "# This file is auto-generated by extract_enums.py in the scripts folder.\n",
        "# You shouldn't edit this file directly.\n",
        "\n",
        "\n",
        "from enum import Enum, IntEnum\n",
        "from typing import Dict\n",
        "\n",
        "\n",
    ]
    for cs_enum, raw_class, nice_class, dict_name in ENUMS:
        python_lines += cs_enums_to_lines(
            all_cs_enums[cs_enum], raw_class, nice_class, dict_name
        )
        if cs_enum != ENUMS[-1][0]:
            python_lines += ["\n"] * 2

    print(f"Writing {gameenums_path} ...")
    with open(gameenums_path, "w", encoding="utf-8", newline="") as fp:
        fp.writelines(python_lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract enums valus from the dump.cs file."
    )
    parser.add_argument("input", type=str, help="Path to the dump.cs file")
    parser.add_argument("output", type=str, help="Path to the gameenums.py file")
    args = parser.parse_args()

    main(args.input, args.output)
