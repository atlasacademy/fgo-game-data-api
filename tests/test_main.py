from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

import orjson
from app.main import app


client = TestClient(app)
file_path = Path(__file__)


def get_response_data(file_name: str) -> Any:
    with open(file_path.parent / "test_data_raw" / f"{file_name}.json", "rb") as fp:
        return orjson.loads(fp.read())


class TestMain:
    def test_home_redirect(self):
        response = client.get("/", allow_redirects=False)
        assert response.status_code == 307
        assert response.headers["Location"] == "/docs"

    def test_JP_export_link(self):
        response = client.get("/export/JP/NiceCard.json")
        assert response.status_code == 200

    def test_NA_export_link(self):
        response = client.get("/export/NA/NiceClassAttackRate.json")
        assert response.status_code == 200
