from pydantic import HttpUrl
from pydantic.tools import parse_obj_as

from ...config import Settings
from ...schemas.common import Region
from ...schemas.nice import AssetURL


settings = Settings()


def get_script_url(region: Region, script_file_name: str) -> HttpUrl:
    if script_file_name[0] in ("0", "9"):
        if script_file_name[:2] == "94":
            script_path = f"94/{script_file_name[:4]}/{script_file_name}"
        else:
            script_path = f"{script_file_name[:2]}/{script_file_name}"
    else:
        script_path = f"Common/{script_file_name}"

    url = AssetURL.script.format(
        base_url=settings.asset_url, region=region, script_path=script_path
    )

    return parse_obj_as(HttpUrl, url)  # type: ignore
