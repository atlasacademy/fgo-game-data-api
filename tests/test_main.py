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
        assert response.headers["Location"] == "/docs"

    def test_openapi_gen(self) -> None:
        response = client.get(str(app.openapi_url))
        assert response.status_code == 200

    def test_openapi_gen_cache(self) -> None:
        response = client.get(str(app.openapi_url))
        assert response.status_code == 200

    def test_docs_gen(self) -> None:
        response = client.get("/docs")
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
        assert response_data.pop("NA")
        assert response_data.pop("JP")
        expected_data = dict(**settings.dict(), file_path=str(file_path))
        expected_data = {
            k: str(v)
            if k in ("file_path", "jp_gamedata", "na_gamedata", "github_webhook_secret")
            else v
            for k, v in expected_data.items()
        }
        assert response_data == expected_data
