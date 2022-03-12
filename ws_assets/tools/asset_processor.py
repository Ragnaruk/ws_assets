import asyncio
from datetime import datetime, timedelta
from typing import Callable, Coroutine, Dict, List

import orjson
import sqlalchemy as sa  # type: ignore
from aiohttp import ClientSession
from loguru import logger

from ws_assets.database.tables import Tables
from ws_assets.exceptions import (
    AssetHTTPRequestError,
    AssetParsingError,
    UnknownAssetIDError,
)
from ws_assets.models.asset import Asset, AssetPoint
from ws_assets.tools.db_client import DBClient


class AssetProcessor:
    def __init__(
        self,
        dsn: str,
        http_client: ClientSession,
        db_client: DBClient,
        subscription_handler: Callable[[List[AssetPoint]], Coroutine],
        http_request_timeout: float = 1.0,
    ):
        """
        Main logic for working with assets and asset points.

        To start working with the class we need to call 2 methods:
            `receive_assets_from_database` in order to receive a list of assets from the database
            `start_receiving_asset_points` in order to start receiving assets points from the endpoint

        :param dsn: endpoint with asset data.
        :param http_client: http client.
        :param db_client: database client.
        :param subscription_handler: coroutine that broadcasts asset points to clients.
        :param http_request_timeout: timeout during http requests.
        """

        self._dsn: str = dsn
        self._http_client: ClientSession = http_client
        self._db_client: DBClient = db_client
        self._subscription_handler: Callable[
            [List[AssetPoint]], Coroutine
        ] = subscription_handler
        self._http_request_timeout: float = http_request_timeout

        # Dictionary where assets will be stored
        self._assets_name_to_id: Dict[str, int] = {}
        self._assets_id_to_name: Dict[int, str] = {}

    async def fetch_assets(self) -> List[Asset]:
        """Receive a list of current assets from the database and cache them."""

        raw_assets: List[dict] = await self._db_client.fetchall(
            sa.select([Tables.asset.c.id, Tables.asset.c.symbol.label("name")]).where(
                True
            )
        )
        assets: List[Asset] = [Asset(**raw_asset) for raw_asset in raw_assets]

        # Cache assets
        # Useful during the first request on startup. Probably useless afterwards
        self._assets_name_to_id = {asset.name: asset.id for asset in assets}
        self._assets_id_to_name = {asset.id: asset.name for asset in assets}

        return assets

    async def fetch_asset_history(
        self, asset_id: int, time: int = 30 * 60
    ) -> List[AssetPoint]:
        """
        Receive a list of asset points for the last `time` seconds.

        :param asset_id: asset id.
        :param time: number of seconds.
        """

        if asset_id not in self._assets_id_to_name:
            raise UnknownAssetIDError(asset_id=asset_id)

        raw_asset_points: List[dict] = await self._db_client.fetchall(
            sa.select(
                [
                    Tables.asset.c.symbol.label("assetName"),
                    Tables.point.c.ts.label("time"),
                    Tables.asset.c.id.label("assetId"),
                    Tables.point.c.value,
                ]
            )
            .select_from(
                Tables.point.join(
                    Tables.asset, onclause=Tables.point.c.asset_id == Tables.asset.c.id
                )
            )
            .where(Tables.point.c.ts > datetime.utcnow() - timedelta(seconds=time))
            .where(Tables.asset.c.id == asset_id)
        )
        asset_points: List[AssetPoint] = [
            AssetPoint(**raw_asset_point) for raw_asset_point in raw_asset_points
        ]

        return asset_points

    async def _make_request_to_asset_endpoint(self) -> str:
        """Make a request to the asset endpoint."""

        # HTTP client may be closed during service shutdown
        # Check just in case
        if not self._http_client.closed:
            async with self._http_client.get(
                self._dsn, timeout=self._http_request_timeout
            ) as response:
                if response.ok:
                    page: str = await response.text()
                else:
                    raise AssetHTTPRequestError(
                        code=response.status, response=await response.text()
                    )

            return page
        else:
            # Return empty values in a correct format to avoid further problems
            return 'null({"Rates": []}); '

    def _parse_asset_text(self, text: str) -> Dict[str, List[dict]]:
        """Parse text returned from the asset endpoint."""

        # Assets are returned in a format which is close but not exactly json, so we need to modify it a bit
        # Page format is `null({...}); `, so we need to remove extra symbols
        text = text[5:-3]

        # Then we need to remove extra commas in objects `{...,}`
        text = text.replace(",}", "}")

        try:
            payload: Dict[str, List[dict]] = orjson.loads(text)
        except orjson.JSONDecodeError:
            raise AssetParsingError(text=text)

        return payload

    def _filter_unused_assets(self, asset_points: Dict[str, List[dict]]) -> List[dict]:
        """Filter out unused assets."""

        return [
            rate
            for rate in asset_points["Rates"]
            if rate["Symbol"] in self._assets_name_to_id
        ]

    def _transform_data_to_database_format(self, asset_points: List[dict]):
        """
        Transform data to the format used by the database.

        Change some field names and calculate `value` field.
        """

        return [
            {
                "asset_id": self._assets_name_to_id[point["Symbol"]],
                "value": (float(point["Bid"]) + float(point["Ask"])) / 2,
            }
            for point in asset_points
        ]

    async def _receive_asset_point(self):
        """Receive an assets' points and write them to the database."""

        try:
            text: str = await self._make_request_to_asset_endpoint()
            all_asset_points: Dict[str, List[dict]] = self._parse_asset_text(text=text)
            useful_asset_points: List[dict] = self._filter_unused_assets(
                asset_points=all_asset_points
            )
            values: List[dict] = self._transform_data_to_database_format(
                asset_points=useful_asset_points
            )

            if values:
                # DB query and websocket can't be parallelized since timestamp
                # is generated in SQLAlchemy model. It can be changed, though, and
                # rather easily
                raw_asset_points: List[dict] = await self._db_client.fetchall(
                    Tables.point.insert()
                    .values(values)
                    .returning(
                        Tables.point.c.asset_id.label("assetId"),
                        Tables.point.c.value,
                        Tables.point.c.ts.label("time"),
                    )
                )
                asset_points: List[AssetPoint] = [
                    AssetPoint(
                        **raw_asset_point,
                        assetName=self._assets_id_to_name[raw_asset_point["assetId"]]
                    )
                    for raw_asset_point in raw_asset_points
                ]

                # WebsocketManager.broadcast_asset_points blocks execution until
                # all data is broadcast to all websockets, but it is fine
                await self._subscription_handler(asset_points)
        except Exception as e:
            logger.exception(e)

            raise e

    async def start_receiving_asset_points(self):
        """Start an endless loop which receives data points every second."""

        while True:
            # In order to receive data every second instead of every `time of execution + 1` seconds
            # we need to launch logic in another task
            # This will still wait for more than 1 second, but I'm unsure than further precision
            # is necessary
            asyncio.create_task(self._receive_asset_point())

            await asyncio.sleep(1)
