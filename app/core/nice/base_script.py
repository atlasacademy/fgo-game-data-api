from pydantic import HttpUrl

from ...config import Settings
from ...data.script import get_script_path
from ...schemas.base import HttpUrlAdapter
from ...schemas.common import Region, ScriptLink
from ...schemas.nice import AssetURL


settings = Settings()


def get_script_url(region: Region, script_file_name: str) -> HttpUrl:
    url = AssetURL.script.format(
        base_url=settings.asset_url,
        region=region,
        script_path=get_script_path(script_file_name),
    )

    return HttpUrlAdapter.validate_python(url)


def get_nice_script_link(region: Region, script_file_name: str) -> ScriptLink:
    return ScriptLink(
        scriptId=script_file_name, script=get_script_url(region, script_file_name)
    )
