from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


def test_web_ui_is_served() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "IRIS Security RAG" in response.text
    assert f'data-api-prefix="{settings.api_v1_prefix}"' in response.text


def test_web_static_assets_are_served() -> None:
    stylesheet = client.get("/static/styles.css")
    script = client.get("/static/app.js")

    assert stylesheet.status_code == 200
    assert script.status_code == 200
    assert "text/css" in stylesheet.headers["content-type"]
    assert "javascript" in script.headers["content-type"]
    assert "fetch(`${apiPrefix}/query`" in script.text
