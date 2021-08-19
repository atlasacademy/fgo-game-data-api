import re

from pydantic import HttpUrl
from pydantic.tools import parse_obj_as

from ...config import Settings
from ...schemas.common import NiceQuestScript, Region
from ...schemas.nice import AssetURL, NiceScriptSearchResult
from ...schemas.raw import ScriptSearchResult


settings = Settings()


def strip_script_formatting(sentence: str) -> str:
    stripped = sentence.strip()
    removed_brackets = re.sub(r"[\[].*?[\]]", " ", stripped)
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
    if script_file_name == "WarEpilogue108.txt":
        return "01/WarEpilogue108.txt"
    if script_file_name[0] in ("0", "9"):
        if script_file_name[:2] == "94":
            return f"94/{script_file_name[:4]}/{script_file_name}"
        else:
            return f"{script_file_name[:2]}/{script_file_name}"
    else:
        return f"Common/{script_file_name}"


def get_script_url(region: Region, script_file_name: str) -> HttpUrl:

    url = AssetURL.script.format(
        base_url=settings.asset_url,
        region=region,
        script_path=get_script_path(script_file_name),
    )

    out_url: HttpUrl = parse_obj_as(HttpUrl, url)

    return out_url


def get_nice_quest_script(region: Region, script_file_name: str) -> NiceQuestScript:
    return NiceQuestScript(
        scriptId=script_file_name, script=get_script_url(region, script_file_name)
    )


def get_nice_script_search_result(
    region: Region, search_result: ScriptSearchResult
) -> NiceScriptSearchResult:
    return NiceScriptSearchResult(
        scriptId=search_result.scriptId,
        script=get_script_url(region, search_result.scriptId),
        score=search_result.score,
        snippets=search_result.snippets,
    )
