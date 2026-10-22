from app.core.config import settings


def test_settings_loaded() -> None:
    assert settings.app_name
    assert settings.database_url
    assert settings.qdrant_url
    assert settings.redis_url
    assert settings.chunk_size > 0
    assert settings.chunk_overlap >= 0
