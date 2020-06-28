from pathlib import Path
from typing import Any

import orjson


file_path = Path(__file__)


def get_response_data(folder: str, file_name: str) -> Any:
    with open(file_path.parent / folder / f"{file_name}.json", "rb") as fp:
        return orjson.loads(fp.read())
