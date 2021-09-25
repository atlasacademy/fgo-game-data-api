from typing import Any, Optional

import orjson
from aioredis import Redis
from fastapi import APIRouter, BackgroundTasks, Depends, Response
from git import Repo  # type: ignore
from sqlalchemy.ext.asyncio import AsyncEngine
from pydantic import BaseModel

from ..config import Settings, project_root
from ..core.info import get_all_repo_info
from ..schemas.common import Region, RepoInfo
from ..tasks import pull_and_update
from .deps import get_async_engines, get_redis
from .utils import pretty_print_response


settings = Settings()


router = APIRouter(
    prefix=f"/{settings.github_webhook_secret.get_secret_value()}"
    if settings.github_webhook_secret.get_secret_value() != ""
    else "",
    include_in_schema=False,
)


repo = Repo(project_root)
latest_commit = repo.commit()
app_info = RepoInfo(
    hash=latest_commit.hexsha[:6],
    timestamp=latest_commit.committed_date,  # pyright: reportGeneralTypeIssues=false
)
app_settings_str = orjson.loads(settings.json())
instance_info = dict(
    app_version=app_info.dict(),
    app_settings=app_settings_str,
    file_path=str(project_root),
)


async def get_secret_info(redis: Redis) -> dict[str, Any]:
    all_repo_info = await get_all_repo_info(redis, settings.data.keys())
    response_data = dict(
        data_repo_version={k.value: v.dict() for k, v in all_repo_info.items()},
        **instance_info,
    )
    return response_data


class GithubWebhookPayload(BaseModel):
    ref: str


@router.post("/update")  # pragma: no cover
async def update_gamedata(
    background_tasks: BackgroundTasks,
    payload: Optional[GithubWebhookPayload],
    async_engines: dict[Region, AsyncEngine] = Depends(get_async_engines),
    redis: Redis = Depends(get_redis),
) -> Response:
    if payload:
        for region, region_data in settings.data.items():
            if payload.ref == f"refs/heads/{region.name}":
                region_pathes = {region: region_data.gamedata}
                break
    else:
        region_pathes = {
            region: region_data.gamedata
            for region, region_data in settings.data.items()
        }
    background_tasks.add_task(pull_and_update, region_pathes, async_engines, redis)
    response_data = await get_secret_info(redis)
    response_data["message"] = "Game data is being updated in the background"
    return pretty_print_response(response_data)


@router.get("/info")
async def info(redis: Redis = Depends(get_redis)) -> Response:
    response_data = await get_secret_info(redis)
    return pretty_print_response(response_data)
