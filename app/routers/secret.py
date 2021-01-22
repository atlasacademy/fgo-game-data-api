from fastapi import APIRouter, BackgroundTasks, Response
from git import Repo

from ..config import Settings, project_root
from ..tasks import RepoInfo, pull_and_update, repo_info
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
app_settings_str = {
    k: str(v) if k in ("jp_gamedata", "na_gamedata", "github_webhook_secret") else v
    for k, v in settings.dict().items()
}
instance_info = dict(
    game_data={k: v.dict() for k, v in repo_info.items()},
    app_version=app_info.dict(),
    app_settings=app_settings_str,
    file_path=str(project_root),
)


@router.post("/update")  # pragma: no cover
async def update_gamedata(background_tasks: BackgroundTasks) -> Response:
    background_tasks.add_task(pull_and_update)
    response_data = dict(
        message="Game data is being updated in the background", **instance_info
    )
    response = pretty_print_response(response_data)
    response.headers["Bloom-Response-Ignore"] = "1"
    return response


@router.get("/info")
async def info() -> Response:
    response = pretty_print_response(instance_info)
    response.headers["Bloom-Response-Ignore"] = "1"
    return response
