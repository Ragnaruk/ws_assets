import functools
import time
from typing import List

import orjson
import sqlalchemy as sa  # type: ignore
from loguru import logger
from sqlalchemy.engine import CursorResult, Row, make_url  # type: ignore
from sqlalchemy.ext.asyncio import (  # type: ignore
    AsyncConnection,
    AsyncEngine,
    create_async_engine,
)

from ws_assets.tools.meta.base_client import BaseClient


def log_query(func):
    """Log database query."""

    @functools.wraps(func)
    async def wrapper(self, query, connection: AsyncConnection = None):
        # Datetime compilation is not implemented, so we simply ignore those queries
        compiled_query: str
        try:
            compiled_query = query.compile(
                dialect=self.engine.dialect, compile_kwargs={"literal_binds": True}
            ).string.replace("\n", "")
        except Exception as e:
            compiled_query = str(query)

        logger.debug(f"Started DB query: {compiled_query}.")

        time_begin: float = time.time()

        results = await func(self, query=query, connection=connection)

        execution_time: float = time.time() - time_begin

        logger.debug(
            f"Finished DB query in {execution_time} seconds. Results: {str(results).replace('{', '{{').replace('}', '}}')}"
        )

        return results

    return wrapper


def start_connection(func):
    """Start a connection if connection is None."""

    @functools.wraps(func)
    async def wrapper(self, query, connection=None):
        if connection:
            return await func(self, query=query, connection=connection)
        else:
            async with self.engine.begin() as connection:
                return await func(self, query=query, connection=connection)

    return wrapper


class DBClient(BaseClient):
    def __init__(self, dsn: str, pool_size: int):
        """
        Database client.

        :param dsn: database dsn.
        :param pool_size: maximum number of connections in the pool.
        """

        self._dsn: str = dsn
        self.pool_size: int = pool_size

        self.engine: AsyncEngine

    async def open(self):
        """Start the database client."""

        self.engine = create_async_engine(
            self._dsn,
            json_deserializer=orjson.loads,
            pool_size=self.pool_size,
            pool_pre_ping=True,
        )

        async with self.engine.begin() as connection:
            await connection.execute(sa.select(sa.text("1")))

        logger.info(
            f"Established connection to the database: {make_url(self._dsn).render_as_string()}"
        )

    async def close(self):
        """Stop the database client."""

        await self.engine.dispose()

        logger.info(
            f"Closed connection to the database: {make_url(self._dsn).render_as_string()}"
        )

    def _transform_to_dict(self, element: Row):
        """Transform Row to dict. Default `dict(row)` uses non-str keys."""

        return {str(k): v for k, v in element._mapping.items()}

    @log_query
    @start_connection
    async def fetchone(self, query, connection: AsyncConnection) -> dict:
        """
        Execute a query and fetch a single row if query returns results.

        :param query: SQLAlchemy query.
        :param connection: SQLAlchemy connection.
        :return:
        """

        cursor: CursorResult = await connection.execute(query)

        results: dict
        if cursor.returns_rows:
            row = cursor.fetchone()
            results = self._transform_to_dict(row) if row else {}
        else:
            results = {}

        return results

    @log_query
    @start_connection
    async def fetchall(self, query, connection: AsyncConnection) -> List[dict]:
        """
        Execute a query and fetch all rows if query returns results.

        :param query: SQLAlchemy query.
        :param connection: SQLAlchemy connection.
        :return:
        """

        cursor: CursorResult = await connection.execute(query)

        results: List[dict]
        if cursor.returns_rows:
            rows = cursor.fetchall()
            results = [self._transform_to_dict(row) for row in rows]
        else:
            results = []

        return results
