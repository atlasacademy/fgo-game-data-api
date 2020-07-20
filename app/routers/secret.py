from pathlib import Path

from fastapi import APIRouter, BackgroundTasks

from ..config import Settings
from ..data.tasks import pull_and_update, repo_info
from .utils import pretty_print_response


file_path = Path(__file__).resolve().parents[2]
router = APIRouter()
settings = Settings()


instance_info = dict(**repo_info, **settings.dict(), file_path=str(file_path))
instance_info = {
    k: str(v)
    if k in ("file_path", "jp_gamedata", "na_gamedata", "github_webhook_secret")
    else v
    for k, v in instance_info.items()
}


@router.post("/update", include_in_schema=False)  # pragma: no cover
async def update_gamedata(background_tasks: BackgroundTasks):
    background_tasks.add_task(pull_and_update)
    response = dict(message="Game data is updated in the background", **instance_info)
    return pretty_print_response(response)


@router.get("/info", include_in_schema=False)
async def info():
    return pretty_print_response(instance_info)
