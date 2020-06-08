from app.config import Settings


class TestSettings:
    def test_url_trim_slash(self, monkeypatch):
        monkeypatch.setenv("ASSET_URL", "https://example.com/assets/")
        settings = Settings()
        assert settings.asset_url == "https://example.com/assets"

    def test_url_trim_slash_no_shash(self, monkeypatch):
        monkeypatch.setenv("ASSET_URL", "https://example.com/assets")
        settings = Settings()
        assert settings.asset_url == "https://example.com/assets"
