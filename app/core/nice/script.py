from sqlalchemy.ext.asyncio import AsyncConnection

from ...config import Settings
from ...schemas.common import Language, Region
from ...schemas.nice import NiceQuest, NiceScript, NiceScriptSearchResult
from ...schemas.raw import ScriptSearchResult
from ..raw import get_script_entity
from .base_script import get_script_url
from .quest import get_nice_quest


settings = Settings()


def get_nice_script_search_result(
    region: Region, search_result: ScriptSearchResult
) -> NiceScriptSearchResult:
    return NiceScriptSearchResult(
        scriptId=search_result.scriptId,
        script=get_script_url(region, search_result.scriptId),
        score=search_result.score,
        snippets=search_result.snippets,
    )


async def get_nice_script(
    conn: AsyncConnection, region: Region, script_id: str, lang: Language
) -> NiceScript:
    raw_script = await get_script_entity(conn, script_id)

    quests = [
        NiceQuest.parse_obj(await get_nice_quest(conn, region, quest, lang))
        for quest in raw_script.quests
    ]

    return NiceScript(
        scriptId=script_id,
        scriptSizeBytes=raw_script.scriptSizeBytes,
        script=get_script_url(region, script_id),
        quests=quests,
    )
