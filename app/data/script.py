import re


brackets_regex = re.compile(r"[\[].*?[\]]")
ruby_regex = re.compile(r"[\[]#(.*):(.*)?[\]]")


def strip_script_formatting(sentence: str) -> str:
    stripped = sentence.strip()
    replaced_ruby = re.sub(ruby_regex, r"\1\2", stripped)
    removed_brackets = re.sub(brackets_regex, " ", replaced_ruby)
    return removed_brackets.replace("\u3000", " ")


def get_script_text_only(script: str) -> str:
    lines = script.split("\n")

    script_lines: list[str] = []
    in_recording_mode = False
    for line in lines:
        if line.startswith("＠"):
            if len(line) >= 3 and line[2] == "：":
                script_lines.append(strip_script_formatting(line[3:]))
            else:
                script_lines.append(strip_script_formatting(line[1:]))
        if line.startswith("？") and "：" in line:
            script_lines.append(strip_script_formatting(line.split("：")[1]))
        if not in_recording_mode:
            if line.startswith("＠"):
                in_recording_mode = True
                continue
        elif line.startswith("[k]") or line.startswith("[page]"):
            in_recording_mode = False
            continue
        else:
            script_lines.append(strip_script_formatting(line))

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
