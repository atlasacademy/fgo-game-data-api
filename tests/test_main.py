from pathlib import Path

import pytest
from httpx import AsyncClient

from app.config import Settings
from app.main import app


file_path = Path(__file__).resolve().parents[1]
settings = Settings()


@pytest.mark.asyncio
class TestMain:
    async def test_home_redirect(self) -> None:
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["Location"] == "/rapidoc"

    async def test_openapi_gen(self, client: AsyncClient) -> None:
        response = await client.get(str(app.openapi_url))
        assert response.status_code == 200

    async def test_openapi_gen_cache(self, client: AsyncClient) -> None:
        response = await client.get(str(app.openapi_url))
        assert response.status_code == 200

    async def test_docs_gen(self, client: AsyncClient) -> None:
        response = await client.get("/docs")
        assert response.status_code == 200

    async def test_rapidoc_gen(self, client: AsyncClient) -> None:
        response = await client.get("/rapidoc")
        assert response.status_code == 200

    async def test_JP_export_link(self, client: AsyncClient) -> None:
        response = await client.get("/export/JP/NiceCard.json")
        assert response.status_code == 200

    async def test_NA_export_link(self, client: AsyncClient) -> None:
        response = await client.get("/export/NA/NiceClassAttackRate.json")
        assert response.status_code == 200

    async def test_info(self, client: AsyncClient) -> None:
        response = (await client.get("/info")).json()
        assert len(response["NA"]["hash"]) == 6
        assert response["JP"]["timestamp"] > 1594450000

    @pytest.mark.skipif(
        settings.github_webhook_secret.get_secret_value() == "",
        reason="Secret path not set",
    )
    async def test_secret_info(self, client: AsyncClient) -> None:
        info_path = f"/{settings.github_webhook_secret.get_secret_value()}/info"
        response = await client.get(info_path)
        assert response.status_code == 200
        response_data = response.json()
        assert "data_repo_version" in response_data
        assert "app_version" in response_data
        assert "app_settings" in response_data
        assert response_data["file_path"] == str(file_path)
