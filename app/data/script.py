import re

from ..schemas.common import Region


brackets_regex = re.compile(r"[\[].*?[\]]")
ruby_regex = re.compile(r"[\[]#(.*):(.*)?[\]]")


def remove_brackets(region: Region, sentence: str) -> str:
    stripped = sentence.replace("\u3000", " ").strip()
    replaced_ruby = re.sub(ruby_regex, r"\1\2", stripped)
    removed_brackets = re.sub(brackets_regex, " ", replaced_ruby)

    if region == Region.JP:
        return removed_brackets.replace(" ", "")

    return removed_brackets


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
            script_lines.append(remove_brackets(region, line.split("：")[1]))

        if not in_recording_mode:
            if line.startswith("＠"):
                in_recording_mode = True
                continue

        elif line.startswith("[k]") or line.startswith("[page]"):
            in_recording_mode = False
            continue
        else:
            script_lines.append(remove_brackets(region, line))

    return " ".join(line for line in script_lines if line != "")


def get_script_path(script_file_name: str) -> str:
    if script_file_name == "WarEpilogue108":
        return "01/WarEpilogue108"
    if script_file_name[0] in ("0", "9"):
        if script_file_name[:2] == "94":
            return f"94/{script_file_name[:4]}/{script_file_name}"
        else:
            return f"{script_file_name[:2]}/{script_file_name}"
    else:
        return f"Common/{script_file_name}"
