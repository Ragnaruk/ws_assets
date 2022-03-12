import asyncio
from datetime import datetime
from typing import Callable, Coroutine, List

import sqlalchemy as sa  # type: ignore

from ws_assets.models.asset import Asset, AssetPoint


class MockAssetProcessor:
    """
    Class that mocks `fetch_assets`, `fetch_asset_history`, and `start_receiving_asset_points` methods.

    Used for testing websocket endpoint.
    """

    def __init__(self, subscription_handler: Callable[[List[AssetPoint]], Coroutine]):
        self._subscription_handler: Callable[
            [List[AssetPoint]], Coroutine
        ] = subscription_handler

    async def fetch_assets(self) -> List[Asset]:
        raw_assets: List[dict] = [
            {"id": 1, "name": "EURUSD"},
            {"id": 2, "name": "USDJPY"},
            {"id": 3, "name": "GBPUSD"},
            {"id": 4, "name": "AUDUSD"},
            {"id": 5, "name": "USDCAD"},
        ]
        assets: List[Asset] = [Asset(**raw_asset) for raw_asset in raw_assets]

        return assets

    async def fetch_asset_history(
        self, asset_id: int, time: int = 30 * 60
    ) -> List[AssetPoint]:
        raw_asset_points: List[dict] = [
            {
                "assetName": "EURUSD",
                "time": 1647092464,
                "assetId": 1,
                "value": 1.0911849999999998,
            },
            {
                "assetName": "EURUSD",
                "time": 1647092464,
                "assetId": 1,
                "value": 0.8911849999999998,
            },
        ]

        asset_points: List[AssetPoint] = [
            AssetPoint(**raw_asset_point) for raw_asset_point in raw_asset_points
        ]

        return asset_points

    async def _receive_asset_point(self):
        """Make a request to the asset endpoint."""

        raw_asset_points: List[dict] = [
            {
                "assetName": "EURUSD",
                "time": 1647092464,
                "assetId": 1,
                "value": 1.0911849999999998,
            },
            {
                "assetName": "USDJPY",
                "time": 1647092464,
                "assetId": 2,
                "value": 0.8911849999999998,
            },
        ]
        asset_points: List[AssetPoint] = [
            AssetPoint(**raw_asset_point) for raw_asset_point in raw_asset_points
        ]

        await self._subscription_handler(asset_points)

    async def start_receiving_asset_points(self):
        """Start an endless loop which receives data points every second."""

        while True:
            # In order to receive data every second instead of every `time of execution + 1` seconds
            # we need to launch logic in another task
            asyncio.create_task(self._receive_asset_point())

            await asyncio.sleep(1)
