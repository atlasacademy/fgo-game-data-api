from fastapi import APIRouter, BackgroundTasks, Response
from git import Repo

from ..config import Settings, project_root
from ..data.tasks import pull_and_update, repo_info
from .utils import pretty_print_response


router = APIRouter()
settings = Settings()


repo = Repo(project_root)
latest_commit = repo.commit()
app_info = {
    "hash": latest_commit.hexsha[:6],
    "timestamp": latest_commit.committed_date,
}


instance_info = dict(
    **repo_info, app=app_info, **settings.dict(), file_path=str(project_root)
)
instance_info = {
    k: str(v)
    if k in ("file_path", "jp_gamedata", "na_gamedata", "github_webhook_secret")
    else v
    for k, v in instance_info.items()
}


@router.post("/update", include_in_schema=False)  # pragma: no cover
async def update_gamedata(background_tasks: BackgroundTasks) -> Response:
    background_tasks.add_task(pull_and_update)
    response = dict(message="Game data is updated in the background", **instance_info)
    return pretty_print_response(response)


@router.get("/info", include_in_schema=False)
async def info() -> Response:
    return pretty_print_response(instance_info)
