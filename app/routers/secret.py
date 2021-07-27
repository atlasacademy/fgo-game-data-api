from fastapi import APIRouter, BackgroundTasks, Depends, Response
from git import Repo
from sqlalchemy.ext.asyncio import AsyncEngine

from ..config import SecretSettings, Settings, project_root
from ..schemas.common import Region, RepoInfo
from ..tasks import REGION_PATHS, pull_and_update, repo_info
from .deps import get_async_engines
from .utils import pretty_print_response


settings = Settings()
secrets = SecretSettings()


router = APIRouter(
    prefix=f"/{secrets.github_webhook_secret.get_secret_value()}"
    if secrets.github_webhook_secret.get_secret_value() != ""
    else "",
    include_in_schema=False,
)


repo = Repo(project_root)
latest_commit = repo.commit()
app_info = RepoInfo(
    hash=latest_commit.hexsha[:6],
    timestamp=latest_commit.committed_date,  # pyright: reportGeneralTypeIssues=false
)
app_settings_str = {
    k: str(v) if k in ("jp_gamedata", "na_gamedata") else v
    for k, v in settings.dict().items()
}
instance_info = dict(
    app_version=app_info.dict(),
    app_settings=app_settings_str,
    file_path=str(project_root),
)


@router.post("/update")  # pragma: no cover
async def update_gamedata(
    background_tasks: BackgroundTasks,
    async_engines: dict[Region, AsyncEngine] = Depends(get_async_engines),
) -> Response:
    background_tasks.add_task(pull_and_update, REGION_PATHS, async_engines)
    response_data = dict(
        message="Game data is being updated in the background",
        game_data={k.value: v.dict() for k, v in repo_info.items()},
        **instance_info,
    )
    response = pretty_print_response(response_data)
    response.headers["Bloom-Response-Ignore"] = "1"
    return response


@router.get("/info")
async def info() -> Response:
    response_data = dict(
        game_data={k.value: v.dict() for k, v in repo_info.items()},
        **instance_info,
    )
    response = pretty_print_response(response_data)
    response.headers["Bloom-Response-Ignore"] = "1"
    return response
