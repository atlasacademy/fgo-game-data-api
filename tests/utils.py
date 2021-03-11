from pathlib import Path
from typing import Any

import orjson
from httpx import AsyncClient, Response

from app.main import app


parent_folder = Path(__file__).parent


def get_response_data(folder: str, file_name: str) -> Any:
    """Return test data given folder and file name"""
    with open(parent_folder / folder / f"{file_name}.json", "rb") as fp:
        return orjson.loads(fp.read())


async def get_response(uri: str) -> Response:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        return await ac.get(uri)
