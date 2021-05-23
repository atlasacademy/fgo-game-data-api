import json
from pathlib import Path
from typing import Literal, Union


file_path = Path(__file__)
MAPPING_PATH = file_path.parent / "mappings"


TRANSLATIONS: dict[str, str] = {}
TRANSLATION_FILES = (
    "skill_names",
    "np_names",
    "event_names",
    "war_names",
    "item_names",
    "entity_names",
    "enemy_names",
    "servant_names",
    "equip_names",
    "cc_names",
    "mc_names",
)

for translation_file in TRANSLATION_FILES:
    with open(MAPPING_PATH / f"{translation_file}.json", "r", encoding="utf-8") as fp:
        TRANSLATIONS |= json.load(fp)

TRANSLATION_FILE_NAMES = Union[
    Literal["skill_names"],
    Literal["np_names"],
    Literal["event_names"],
    Literal["war_names"],
    Literal["item_names"],
    Literal["entity_names"],
    Literal["enemy_names"],
    Literal["servant_names"],
    Literal["equip_names"],
    Literal["cc_names"],
    Literal["mc_names"],
]
with open(MAPPING_PATH / "translation_override.json", "r", encoding="utf-8") as fp:
    TRANSLATION_OVERRIDE: dict[TRANSLATION_FILE_NAMES, dict[str, str]] = json.load(fp)


EXTRA_CHARAFIGURES: dict[int, list[int]] = {}

with open(MAPPING_PATH / "extra_charafigure.json", "r", encoding="utf-8") as fp:
    EXTRA_CHARAFIGURES = {cf["svtId"]: cf["charaFigureIds"] for cf in json.load(fp)}


EXTRA_IMAGES: dict[int, list[Union[int, str]]] = {}

with open(MAPPING_PATH / "extra_image.json", "r", encoding="utf-8") as fp:
    EXTRA_IMAGES = {im["svtId"]: im["imageIds"] for im in json.load(fp)}
