from fastapi import APIRouter

from ws_assets.routes import ui
from ws_assets.routes.api.v1 import websocket
from ws_assets.settings import Settings

settings = Settings()

# /api/v1
api_v1_router = APIRouter(tags=["v1"])

for endpoints in (websocket,):
    api_v1_router.include_router(endpoints.router, prefix="/api/v1")


# UI
ui_router = APIRouter(tags=["UI"])

for endpoints in (ui,):
    ui_router.include_router(endpoints.router)
