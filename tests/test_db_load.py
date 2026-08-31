from typing import Any

import httpx
import pytest
from sqlalchemy import create_engine, select

from app.db.load import (
    AssetManifestSource,
    fetch_asset_manifest,
    fetch_asset_manifests,
    insert_db,
)
from app.models.raw import AssetManifest
from app.schemas.common import Region


def make_manifest_item(**overrides: Any) -> dict[str, Any]:
    item = {
        "fileName": "BGM/bgm_001.mp3",
        "size": 12345,
        "uploadTimestamp": 1730000000000,
        "contentType": "audio/mpeg",
        "contentSHA1": "sha1",
        "contentMD5": "md5",
    }
    item.update(overrides)
    return item


def test_fetch_asset_manifest() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == httpx.URL(
            "https://example.com/GameData/JP/Audio/manifest.json"
        )
        return httpx.Response(200, json=[make_manifest_item(extra="ignored")])

    source = AssetManifestSource("Audio", "Audio/manifest.json")
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        manifest = fetch_asset_manifest(
            client, Region.JP, "https://example.com/GameData/", source
        )

    assert manifest == [
        {
            "manifestId": "Audio",
            "sourceUrl": "https://example.com/GameData/JP/Audio/manifest.json",
            **make_manifest_item(),
        }
    ]


def test_fetch_asset_manifests_combines_sources() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        folder = request.url.path.split("/")[-2]
        return httpx.Response(
            200, json=[make_manifest_item(fileName=f"{folder}/shared-name.bin")]
        )

    sources = (
        AssetManifestSource("Audio", "Audio/manifest.json"),
        AssetManifestSource("External", "External/manifest.json"),
    )
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        manifests = fetch_asset_manifests(
            client, Region.NA, "https://example.com", sources
        )

    assert [(item["manifestId"], item["fileName"]) for item in manifests] == [
        ("Audio", "Audio/shared-name.bin"),
        ("External", "External/shared-name.bin"),
    ]


def test_fetch_asset_manifest_rejects_missing_columns() -> None:
    item = make_manifest_item()
    item.pop("contentMD5")

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[item])

    source = AssetManifestSource("Audio", "Audio/manifest.json")
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(ValueError, match="missing: contentMD5"):
            fetch_asset_manifest(client, Region.NA, "https://example.com", source)


def test_fetch_asset_manifest_rejects_invalid_payload() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"fileName": "not-a-list"})

    source = AssetManifestSource("Audio", "Audio/manifest.json")
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(ValueError, match="is not a list"):
            fetch_asset_manifest(client, Region.JP, "https://example.com", source)


def test_asset_manifest_table_schema() -> None:
    assert list(AssetManifest.columns.keys()) == [
        "manifestId",
        "fileName",
        "sourceUrl",
        "size",
        "uploadTimestamp",
        "contentType",
        "contentSHA1",
        "contentMD5",
    ]
    assert list(AssetManifest.primary_key.columns.keys()) == [
        "manifestId",
        "fileName",
    ]


def test_asset_manifest_load_replaces_previous_data() -> None:
    engine = create_engine("sqlite://")
    shared_file = make_manifest_item(fileName="shared-name.bin")
    initial_data = [
        {
            "manifestId": manifest_id,
            "sourceUrl": f"https://example.com/{manifest_id}/manifest.json",
            **shared_file,
        }
        for manifest_id in ("Audio", "External")
    ]

    with engine.begin() as conn:
        insert_db(conn, AssetManifest, initial_data)
        initial_rows = conn.execute(select(AssetManifest)).mappings().all()

    assert len(initial_rows) == 2

    replacement_data = [
        {
            "manifestId": "Audio",
            "sourceUrl": "https://example.com/Audio/manifest.json",
            **make_manifest_item(fileName="replacement.mp3"),
        }
    ]
    with engine.begin() as conn:
        insert_db(conn, AssetManifest, replacement_data)
        replacement_rows = conn.execute(select(AssetManifest)).mappings().all()

    assert [(row["manifestId"], row["fileName"]) for row in replacement_rows] == [
        ("Audio", "replacement.mp3")
    ]
    engine.dispose()
