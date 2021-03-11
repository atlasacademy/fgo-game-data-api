import argparse
import asyncio

import aiofiles

from .test_basic import test_cases_dict as test_basic_data
from .test_nice import test_cases_dict as test_nice_data
from .test_raw import test_cases_dict as test_raw_data
from .utils import get_response, parent_folder


async def save_test_data(
    endpoint: str, query: str, folder: str, file_name: str
) -> None:
    uri = f"/{endpoint}/{query}"
    print("Getting " + uri)
    data = await get_response(uri)
    async with aiofiles.open(parent_folder / folder / f"{file_name}.json", "wb") as fp:
        await fp.write(data.content)


async def main(
    get_raw: bool = False, get_nice: bool = False, get_basic: bool = False
) -> None:
    print("Saving test data ...")
    if not any([get_raw, get_nice, get_basic]):
        get_raw = get_nice = get_basic = True

    for to_download, query_data, endpoint, folder in (
        (get_raw, test_raw_data, "raw", "test_data_raw"),
        (get_nice, test_nice_data, "nice", "test_data_nice"),
        (get_basic, test_basic_data, "basic", "test_data_basic"),
    ):
        if to_download:
            for query, file_name in query_data.values():
                await save_test_data(endpoint, query, folder, file_name)


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

    args = parser.parse_args()

    asyncio.run(main(args.raw, args.nice, args.basic))
