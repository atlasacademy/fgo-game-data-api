from pydantic import HttpUrl
from pydantic.tools import parse_obj_as

from ...config import Settings
from ...data.script import get_script_path
from ...schemas.common import Region, ScriptLink
from ...schemas.nice import AssetURL


settings = Settings()


def get_script_url(region: Region, script_file_name: str) -> HttpUrl:
    url = AssetURL.script.format(
        base_url=settings.asset_url,
        region=region,
        script_path=get_script_path(script_file_name),
    )

    out_url: HttpUrl = parse_obj_as(HttpUrl, url)

    return out_url


def get_nice_script_link(region: Region, script_file_name: str) -> ScriptLink:
    return ScriptLink(
        scriptId=script_file_name, script=get_script_url(region, script_file_name)
    )
