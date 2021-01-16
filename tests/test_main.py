# pylint: disable=R0201
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app


client = TestClient(app)
file_path = Path(__file__).resolve().parents[1]
settings = Settings()


class TestMain:
    def test_home_redirect(self) -> None:
        response = client.get("/", allow_redirects=False)
        assert response.status_code == 307
        assert response.headers["Location"] == "/rapidoc"

    def test_openapi_gen(self) -> None:
        response = client.get(str(app.openapi_url))
        assert response.status_code == 200

    def test_openapi_gen_cache(self) -> None:
        response = client.get(str(app.openapi_url))
        assert response.status_code == 200

    def test_docs_gen(self) -> None:
        response = client.get("/docs")
        assert response.status_code == 200

    def test_rapidoc_gen(self) -> None:
        response = client.get("/rapidoc")
        assert response.status_code == 200

    def test_JP_export_link(self) -> None:
        response = client.get("/export/JP/NiceCard.json")
        assert response.status_code == 200

    def test_NA_export_link(self) -> None:
        response = client.get("/export/NA/NiceClassAttackRate.json")
        assert response.status_code == 200

    def test_info(self) -> None:
        response = client.get("/info").json()
        assert len(response["NA"]["hash"]) == 6
        assert response["JP"]["timestamp"] > 1594450000

    @pytest.mark.skipif(
        settings.github_webhook_secret == "", reason="Secret path not set"
    )
    def test_secret_info(self) -> None:
        info_path = f"/{settings.github_webhook_secret.get_secret_value()}/info"
        response = client.get(info_path)
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
