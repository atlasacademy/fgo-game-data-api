from typing import Any, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Response
from pydantic import BaseModel

from ..config import Settings, instance_info
from ..core.info import get_all_repo_info
from ..db.engine import async_engines
from ..redis import Redis
from ..tasks import pull_and_update
from .deps import get_redis
from .utils import pretty_print_response


settings = Settings()


router = APIRouter(
    prefix=f"/{settings.github_webhook_secret.get_secret_value()}"
    if settings.github_webhook_secret.get_secret_value() != ""
    else "",
    include_in_schema=False,
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
    payload: Optional[GithubWebhookPayload] = None,
    redis: Redis = Depends(get_redis),
) -> Response:
    region_pathes = {
        region: region_data.gamedata for region, region_data in settings.data.items()
    }
    if payload:
        for region, region_data in settings.data.items():
            if payload.ref == f"refs/heads/{region.name}":
                region_pathes = {region: region_data.gamedata}
                break
    background_tasks.add_task(pull_and_update, region_pathes, async_engines, redis)
    secret_info = await get_secret_info(redis)
    regions = ", ".join(region.name for region in region_pathes)
    response_data = dict(
        message=f"{regions} game data is being updated in the background", **secret_info
    )
    return pretty_print_response(response_data)


@router.get("/info")
async def info(redis: Redis = Depends(get_redis)) -> Response:
    response_data = await get_secret_info(redis)
    return pretty_print_response(response_data)
