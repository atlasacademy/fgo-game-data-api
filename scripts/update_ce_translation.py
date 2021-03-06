import argparse
import json
import os
from pathlib import Path
from typing import Any, Callable, Dict

from dotenv import load_dotenv


MAPPING_PATH = Path(__file__).resolve().parents[1] / "app" / "data" / "mappings"


def get_ce_names(mstSvt: Any) -> Dict[int, str]:
    ce_names: Dict[int, str] = {
        svt["collectionNo"]: svt["name"]
        for svt in mstSvt
        if svt["type"] == 6 and svt["collectionNo"] != 0
    }
    return ce_names


def get_cc_names(mstCommandCode: Any) -> Dict[int, str]:
    cc_names: Dict[int, str] = {
        svt["collectionNo"]: svt["name"] for svt in mstCommandCode
    }
    return cc_names


def update_translation(
    mapping: str,
    jp_master: Path,
    na_master: Path,
    master_file: str,
    extract_names: Callable[[Any], Dict[int, str]],
) -> None:
    with open(jp_master / f"{master_file}.json", "r", encoding="utf-8") as fp:
        jp_svt = json.load(fp)
    with open(na_master / f"{master_file}.json", "r", encoding="utf-8") as fp:
        na_svt = json.load(fp)

    mapping_path = MAPPING_PATH / mapping
    if mapping_path.exists():
        with open(mapping_path, "r", encoding="utf-8") as fp:
            current_translations: Dict[str, str] = json.load(fp)
    else:
        current_translations = {}

    na_names = extract_names(na_svt)
    jp_names = extract_names(jp_svt)

    updated_translation = {
        jp_name: na_names.get(colNo, current_translations.get(jp_name, jp_name))
        for colNo, jp_name in sorted(jp_names.items(), key=lambda x: x[0])
    }

    with open(mapping_path, "w", encoding="utf-8", newline="\n") as fp:
        json.dump(updated_translation, fp, indent=2, ensure_ascii=False)
        fp.write("\n")


def main(jp_master: Path, na_master: Path) -> None:
    update_translation(
        "equip_names.json",
        jp_master,
        na_master,
        "mstSvt",
        get_ce_names,
    )
    update_translation(
        "cc_names.json",
        jp_master,
        na_master,
        "mstCommandCode",
        get_cc_names,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update CE name translation file with NA translations."
    )
    parser.add_argument(
        "--jp-master",
        type=str,
        help="Path to the JP master folder. Not needed if environment variable JP_GAMEDATA is set.",
        default=None,
    )
    parser.add_argument(
        "--na-master",
        type=str,
        help="Path to the NA master folder. Not needed if environment variable NA_GAMEDATA is set.",
        default=None,
    )

    args = parser.parse_args()
    load_dotenv()

    if args.jp_master:
        jp_path = Path(args.jp_master).resolve()
    elif os.getenv("JP_GAMEDATA"):
        jp_path = Path(str(os.getenv("JP_GAMEDATA"))).resolve()
    else:
        raise KeyError("JP_GAMEDATA not found")

    if args.na_master:
        na_path = Path(args.na_master).resolve()
    elif os.getenv("NA_GAMEDATA"):
        na_path = Path(str(os.getenv("NA_GAMEDATA"))).resolve()
    else:
        raise KeyError("NA_GAMEDATA not found")

    main(jp_path, na_path)
