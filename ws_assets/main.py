import asyncio
from pathlib import Path

from aiohttp import ClientSession
from fastapi import FastAPI
from loguru import logger

from alembic import command
from alembic.config import Config
from ws_assets.routers import api_v1_router, ui_router
from ws_assets.settings import Settings
from ws_assets.tools.asset_processor import AssetProcessor
from ws_assets.tools.db_client import DBClient
from ws_assets.tools.websocket_manager import WebsocketManager


def create_app() -> FastAPI:
    try:
        # App
        app = FastAPI(title="WS Asset")

        # Settings
        app.state.Settings = Settings()

        # Routers
        app.include_router(api_v1_router)

        if app.state.Settings.ENABLE_UI:
            app.include_router(ui_router)

        # Middlewares
        ...

        # WebsocketManager
        app.state.WebsocketManager = WebsocketManager()

        # DBClient
        app.state.DBClient = DBClient(
            dsn=app.state.Settings.POSTGRESQL_DSN,
            pool_size=app.state.Settings.POSTGRESQL_POOL_SIZE,
        )

        # ClientSession
        app.state.ClientSession = ClientSession()

        # AssetProcessor
        app.state.AssetProcessor = AssetProcessor(
            dsn=app.state.Settings.ASSETS_DSN,
            http_client=app.state.ClientSession,
            db_client=app.state.DBClient,
            subscription_handler=app.state.WebsocketManager.broadcast_asset_points,
        )

        # Event handlers
        @app.on_event("startup")
        async def startup():
            try:
                # Alembic
                if app.state.Settings.AUTO_APPLY_MIGRATIONS:
                    alembic_config = Config(
                        str(Path(__file__).parent.parent / "alembic.ini")
                    )
                    alembic_config.set_main_option(
                        "script_location", str(Path(__file__).parent.parent / "alembic")
                    )
                    alembic_config.set_main_option(
                        "sqlalchemy.url", app.state.Settings.POSTGRESQL_DSN
                    )
                    command.upgrade(alembic_config, "head")

                # DBClient
                await app.state.DBClient.open()

                # AssetProcessor
                await app.state.AssetProcessor.fetch_assets()
                asyncio.create_task(
                    app.state.AssetProcessor.start_receiving_asset_points()
                )

                print(
                    f"Running on http://{app.state.Settings.HOST}:{app.state.Settings.PORT}"
                )
            except Exception as e:
                logger.exception(e)

                raise e

        @app.on_event("shutdown")
        async def shutdown():
            try:
                # DBClient
                await app.state.DBClient.close()

                # ClientSession
                await app.state.ClientSession.close()

                # Give a chance to coroutines to finish their tasks
                await asyncio.sleep(2)
            except Exception as e:
                logger.exception(e)

                raise e

        return app
    except Exception as e:
        # uvicorn silently ignores errors during app creation,
        # so we need to catch them here
        logger.exception(e)

        raise e
