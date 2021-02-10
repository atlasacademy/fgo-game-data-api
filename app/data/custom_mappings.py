import json
from pathlib import Path
from typing import Dict, List


file_path = Path(__file__)
MAPPING_PATH = file_path.parent / "mappings"


TRANSLATIONS: Dict[str, str] = {}
TRANSLATION_FILES = (
    "servant_names.json",
    "equip_names.json",
    "cc_names.json",
    "mc_names.json",
)

for translation_file in TRANSLATION_FILES:
    with open(MAPPING_PATH / translation_file, "r", encoding="utf-8") as fp:
        TRANSLATIONS.update(json.load(fp))


EXTRA_CHARAFIGURES: Dict[int, List[int]] = {}


with open(MAPPING_PATH / "extra_charafigure.json", "r", encoding="utf-8") as fp:
    EXTRA_CHARAFIGURES = {cf["svtId"]: cf["charaFigureIds"] for cf in json.load(fp)}
