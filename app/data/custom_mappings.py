import json
from pathlib import Path
from typing import Union


file_path = Path(__file__)
MAPPING_PATH = file_path.parent / "mappings"


TRANSLATIONS: dict[str, str] = {}
TRANSLATION_FILES = (
    "servant_names.json",
    "equip_names.json",
    "cc_names.json",
    "mc_names.json",
)

for translation_file in TRANSLATION_FILES:
    with open(MAPPING_PATH / translation_file, "r", encoding="utf-8") as fp:
        TRANSLATIONS |= json.load(fp)


EXTRA_CHARAFIGURES: dict[int, list[int]] = {}

with open(MAPPING_PATH / "extra_charafigure.json", "r", encoding="utf-8") as fp:
    EXTRA_CHARAFIGURES = {cf["svtId"]: cf["charaFigureIds"] for cf in json.load(fp)}


EXTRA_IMAGES: dict[int, list[Union[int, str]]] = {}

with open(MAPPING_PATH / "extra_image.json", "r", encoding="utf-8") as fp:
    EXTRA_IMAGES = {im["svtId"]: im["imageIds"] for im in json.load(fp)}
