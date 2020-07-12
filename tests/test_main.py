from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
file_path = Path(__file__)


class TestMain:
    def test_home_redirect(self):
        response = client.get("/", allow_redirects=False)
        assert response.status_code == 307
        assert response.headers["Location"] == "/docs"

    def test_openapi_gen(self):
        response = client.get(str(app.openapi_url))
        assert response.status_code == 200

    def test_openapi_gen_cache(self):
        response = client.get(str(app.openapi_url))
        assert response.status_code == 200

    def test_docs_gen(self):
        response = client.get("/docs")
        assert response.status_code == 200

    def test_JP_export_link(self):
        response = client.get("/export/JP/NiceCard.json")
        assert response.status_code == 200

    def test_NA_export_link(self):
        response = client.get("/export/NA/NiceClassAttackRate.json")
        assert response.status_code == 200

    def test_info(self):
        response = client.get("/info").json()
        assert len(response["NA"]["hash"]) == 6
        assert response["JP"]["timestamp"] > 1594450000
