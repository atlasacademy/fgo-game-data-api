import re

from ..schemas.common import Region


brackets_regex = re.compile(r"[\[].*?[\]]")
ruby_regex = re.compile(r"[\[]#(.*?):(.*?)?[\]]")
ruby_emphasis_regex = re.compile(r"\[#(.*?)\]")
gender_regex = re.compile(r"[\[]&(.*?):(.*?)?[\]]")


def remove_brackets(region: Region, sentence: str) -> str:
    replaced_full_width_space = sentence.replace("\u3000", " ")
    replaced_ruby = re.sub(ruby_regex, r"\1 \2", replaced_full_width_space)
    replaced_ruby_emphasis = re.sub(ruby_emphasis_regex, r"\1", replaced_ruby)
    removed_brackets = re.sub(brackets_regex, " ", replaced_ruby_emphasis)
    stripped = removed_brackets.strip()

    if region != Region.NA:
        return stripped.replace(" ", "")

    return stripped


def get_script_text_only(region: Region, script: str) -> str:
    lines = script.split("\n")

    script_lines: list[str] = []
    in_recording_mode = False
    for line in lines:
        if line.startswith("＠"):
            if len(line) >= 3 and line[2] == "：":
                name = remove_brackets(region, line[3:])
            else:
                name = remove_brackets(region, line[1:])
            script_lines.append(f"({name})")

        if line.startswith("？") and "：" in line:
            script_lines.append("(Choice)")
            script_lines.append(remove_brackets(region, line.split("：")[1]))

        if not in_recording_mode:
            if line.startswith("＠"):
                in_recording_mode = True
                continue

        elif line.startswith(("[page]", "[k]")):
            in_recording_mode = False
            continue
        elif "[&" in line:
            male_line = remove_brackets(region, re.sub(gender_regex, r"\1", line))
            female_line = remove_brackets(region, re.sub(gender_regex, r"\2", line))
            script_lines.append(f"(Male) {male_line} (Female) {female_line}")
        else:
            script_lines.append(remove_brackets(region, line))

    return " ".join(line for line in script_lines if line != "")


def get_script_path(script_file_name: str) -> str:
    if script_file_name == "WarEpilogue108":
        return "01/WarEpilogue108"
    if len(script_file_name) > 0 and script_file_name[0] in ("0", "9"):
        if script_file_name[:2] == "94":
            return f"94/{script_file_name[:4]}/{script_file_name}"
        else:
            return f"{script_file_name[:2]}/{script_file_name}"
    else:
        return f"Common/{script_file_name}"
