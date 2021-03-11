# pylint: disable=R0201
from pathlib import Path

import pytest
from httpx import AsyncClient

from app.config import Settings
from app.main import app

from .utils import get_response


file_path = Path(__file__).resolve().parents[1]
settings = Settings()


@pytest.mark.asyncio
class TestMain:
    async def test_home_redirect(self) -> None:
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/", allow_redirects=False)
        assert response.status_code == 307
        assert response.headers["Location"] == "/rapidoc"

    async def test_openapi_gen(self) -> None:
        response = await get_response(str(app.openapi_url))
        assert response.status_code == 200

    async def test_openapi_gen_cache(self) -> None:
        response = await get_response(str(app.openapi_url))
        assert response.status_code == 200

    async def test_docs_gen(self) -> None:
        response = await get_response("/docs")
        assert response.status_code == 200

    async def test_rapidoc_gen(self) -> None:
        response = await get_response("/rapidoc")
        assert response.status_code == 200

    async def test_JP_export_link(self) -> None:
        response = await get_response("/export/JP/NiceCard.json")
        assert response.status_code == 200

    async def test_NA_export_link(self) -> None:
        response = await get_response("/export/NA/NiceClassAttackRate.json")
        assert response.status_code == 200

    async def test_info(self) -> None:
        response = (await get_response("/info")).json()
        assert len(response["NA"]["hash"]) == 6
        assert response["JP"]["timestamp"] > 1594450000

    @pytest.mark.skipif(
        settings.github_webhook_secret.get_secret_value() == "",
        reason="Secret path not set",
    )
    async def test_secret_info(self) -> None:
        info_path = f"/{settings.github_webhook_secret.get_secret_value()}/info"
        response = await get_response(info_path)
        assert response.status_code == 200
        response_data = response.json()
        assert "game_data" in response_data
        assert "app_version" in response_data
        assert response_data["file_path"] == str(file_path)
        expected_data = {
            k: str(v)
            if k in ("jp_gamedata", "na_gamedata", "github_webhook_secret")
            else v
            for k, v in settings.dict().items()
        }
        assert response_data["app_settings"] == expected_data
