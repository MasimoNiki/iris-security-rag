from fastapi import APIRouter

from app.api.v1.endpoints import health, query, search

api_router = APIRouter()

api_router.include_router(
    health.router,
    tags=["Health"],
)

api_router.include_router(
    search.router,
    tags=["Search"],
)

api_router.include_router(
    query.router,
    tags=["Query"],
)
