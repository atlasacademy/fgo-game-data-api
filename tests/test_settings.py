from _pytest.monkeypatch import MonkeyPatch

from app.config import Settings


class TestSettings:
    def test_url_trim_slash(self, monkeypatch: MonkeyPatch) -> None:
        monkeypatch.setenv("ASSET_URL", "https://example.com/assets/")
        settings = Settings()
        assert str(settings.asset_url) == "https://example.com/assets"

    def test_url_trim_slash_no_shash(self, monkeypatch: MonkeyPatch) -> None:
        monkeypatch.setenv("ASSET_URL", "https://example.com/assets")
        settings = Settings()
        assert str(settings.asset_url) == "https://example.com/assets"
