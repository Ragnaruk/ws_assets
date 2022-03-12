from typing import List, Literal

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    # Service
    HOST: str = Field("0.0.0.0", env="WS_ASSETS_HOST", description="Service host.")
    PORT: int = Field("8080", env="WS_ASSETS_PORT", description="Service port.")

    ENABLE_UI: bool = Field(
        "TRUE", env="WS_ASSETS_ENABLE_UI", description="Enable UI on / path."
    )
    AUTO_APPLY_MIGRATIONS: bool = Field(
        "TRUE",
        env="WS_ASSETS_AUTO_APPLY_MIGRATIONS",
        description="Automatically apply database migrations on service start.",
    )

    # Assets
    ASSETS_DSN: str = Field(
        "https://ratesjson.fxcm.com/DataDisplayer",
        description="A full path to the endpoint which returns asset data.",
    )

    # Logging
    LOG_LEVEL: Literal[
        "CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "TRACE"
    ] = Field("INFO", env="WS_ASSETS_LOG_LEVEL", description="Logging level.")

    # PostgreSQL
    POSTGRESQL_DSN: str = Field(
        "postgresql+asyncpg://user:password@localhost:5432/database",
        env="WS_ASSETS_POSTGRESQL_DSN",
        description="PostgreSQL DSN.",
    )
    POSTGRESQL_POOL_SIZE: int = Field(
        "10",
        env="WS_ASSETS_POSTGRESQL_POOL_SIZE",
        description="PostgreSQL maximum pool size.",
    )

    @classmethod
    def get_documentation(cls) -> str:
        """Generate a markdown table of environmental variables."""

        lines: List[str] = []

        # Get all useful information from Settings
        for variable in Settings().schema()["properties"].values():
            if "env" in variable:
                lines.append(
                    f"{variable['env']}: {variable['description']} (\"{variable['default']}\")"
                )

        return "\n".join(lines)


if __name__ == "__main__":
    print(Settings.get_documentation())
