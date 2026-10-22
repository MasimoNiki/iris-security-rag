from html import escape
from pathlib import Path

from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import SessionLocal
from app.services.observability.metrics import update_ingestion_metrics_from_db

WEB_DIR = Path(__file__).resolve().parent / "web"
INDEX_TEMPLATE_PATH = WEB_DIR / "templates" / "index.html"


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        version="0.1.0",
        description="RAG system for SOC and information security knowledge base",
    )

    app.include_router(
        api_router,
        prefix=settings.api_v1_prefix,
    )

    app.mount(
        "/static",
        StaticFiles(directory=WEB_DIR / "static"),
        name="static",
    )

    @app.get("/", include_in_schema=False, response_class=HTMLResponse)
    def web_ui() -> HTMLResponse:
        template = INDEX_TEMPLATE_PATH.read_text(encoding="utf-8")
        api_prefix = escape(settings.api_v1_prefix.rstrip("/"), quote=True)
        return HTMLResponse(template.replace("{{ api_v1_prefix }}", api_prefix))

    @app.get("/metrics", include_in_schema=False)
    def metrics() -> Response:
        db = SessionLocal()

        try:
            update_ingestion_metrics_from_db(db)
            metrics_content = generate_latest()
        finally:
            db.close()

        return Response(
            content=metrics_content,
            media_type=CONTENT_TYPE_LATEST,
        )

    return app


app = create_app()
