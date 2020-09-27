import json
from pathlib import Path
from typing import Dict


file_path = Path(__file__)
MAPPING_PATH = file_path.parent / "mappings"


TRANSLATIONS: Dict[str, str] = {}


for translation_file in ("servant_names.json", "equip_names.json"):
    with open(MAPPING_PATH / translation_file, "r", encoding="utf-8") as fp:
        TRANSLATIONS.update(json.load(fp))
