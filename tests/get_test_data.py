import argparse
import asyncio
import platform

import aiofiles
import orjson
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from app.main import app

from .test_basic import test_cases_dict as test_basic_data
from .test_nice import test_cases_dict as test_nice_data
from .test_raw import test_cases_dict as test_raw_data
from .utils import clear_drop_data, parent_folder


async def save_test_data(
    client: AsyncClient, endpoint: str, query: str, folder: str, file_name: str
) -> None:
    uri = f"/{endpoint}/{query}"
    print("Getting " + uri)
    response = await client.get(uri)
    async with aiofiles.open(parent_folder / folder / f"{file_name}.json", "wb") as fp:
        if "quest" in query and endpoint == "nice" and len(query.split("/")) == 4:
            quest_phase_data = response.json()
            cleared_drop_data = clear_drop_data(quest_phase_data)
            await fp.write(orjson.dumps(cleared_drop_data))
        else:
            await fp.write(response.content)


async def main(
    get_raw: bool = False,
    get_nice: bool = False,
    get_basic: bool = False,
    test: str | None = None,
) -> None:
    print("Saving test data ...")
    if not any([get_raw, get_nice, get_basic]):
        get_raw = get_nice = get_basic = True

    async with (
        LifespanManager(app, startup_timeout=60),
        AsyncClient(app=app, base_url="http://test") as ac,
    ):
        for to_download, query_data, endpoint, folder in (
            (get_raw, test_raw_data, "raw", "test_data_raw"),
            (get_nice, test_nice_data, "nice", "test_data_nice"),
            (get_basic, test_basic_data, "basic", "test_data_basic"),
        ):
            if to_download:
                if test and test in query_data:
                    query, file_name = query_data[test]
                    await save_test_data(ac, endpoint, query, folder, file_name)
                else:
                    for query, file_name in query_data.values():
                        await save_test_data(ac, endpoint, query, folder, file_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Save test data to test_data folders.")
    parser.add_argument(
        "--raw",
        action="store_true",
        required=False,
        default=False,
        help="Save raw test data",
    )
    parser.add_argument(
        "--nice",
        action="store_true",
        required=False,
        default=False,
        help="Save nice test data",
    )
    parser.add_argument(
        "--basic",
        action="store_true",
        required=False,
        default=False,
        help="Save basic test data",
    )
    parser.add_argument(
        "-t",
        "--test",
        type=str,
        required=False,
        default=None,
        help="Specific test to save",
    )

    args = parser.parse_args()

    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main(args.raw, args.nice, args.basic, args.test))
