import uvicorn  # type: ignore

from ws_assets.settings import Settings

if __name__ == "__main__":
    settings = Settings()

    uvicorn.run(
        "ws_assets.main:create_app",
        host=settings.HOST,
        port=settings.PORT,
        log_level="error",
    )
