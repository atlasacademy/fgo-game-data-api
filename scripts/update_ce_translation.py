import argparse
import json
import os
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv


def main(
    mapping: str, jp_master: Optional[str] = None, na_master: Optional[str] = None
) -> None:
    load_dotenv()

    if jp_master:
        jp_path = Path(jp_master).resolve()
    elif os.getenv("JP_GAMEDATA"):
        jp_path = Path(str(os.getenv("JP_GAMEDATA"))).resolve()
    else:
        raise KeyError("JP_GAMEDATA not foound")

    if na_master:
        na_path = Path(na_master).resolve()
    elif os.getenv("NA_GAMEDATA"):
        na_path = Path(str(os.getenv("NA_GAMEDATA"))).resolve()
    else:
        raise KeyError("NA_GAMEDATA not foound")

    with open(jp_path / "mstSvt.json", "r", encoding="utf-8") as fp:
        jp_svt = json.load(fp)
    with open(na_path / "mstSvt.json", "r", encoding="utf-8") as fp:
        na_svt = json.load(fp)
    with open(mapping, "r", encoding="utf-8") as fp:
        ce_translations: Dict[str, str] = json.load(fp)

    na_names: Dict[int, str] = {
        item["collectionNo"]: item["name"]
        for item in na_svt
        if item["type"] == 6 and item["collectionNo"] != 0
    }
    jp_names: Dict[int, str] = {
        item["collectionNo"]: item["name"]
        for item in jp_svt
        if item["type"] == 6 and item["collectionNo"] != 0
    }

    updated_ce_translation = {
        jp_name: na_names.get(colNo, ce_translations.get(jp_name, ""))
        for colNo, jp_name in sorted(jp_names.items(), key=lambda x: x[0])
    }

    with open(mapping, "w", encoding="utf-8", newline="\n") as fp:
        fp.write(
            json.dumps(updated_ce_translation, indent=2, ensure_ascii=False) + "\n"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update CE name translation file with NA translations."
    )
    parser.add_argument("--mapping", type=str, help="Path to the equip_names.json file")
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

    main(args.mapping, args.jp_master, args.na_master)
