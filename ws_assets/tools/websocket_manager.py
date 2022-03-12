import asyncio
from typing import Dict, List
from uuid import UUID

from starlette.websockets import WebSocket

from ws_assets.models.asset import Asset, AssetPoint
from ws_assets.models.client import WebsocketClient
from ws_assets.models.response import (
    ResponseAssets,
    ResponseAssetsMessage,
    ResponseError,
    ResponseErrorMessage,
    ResponseSubscribeHistory,
    ResponseSubscribeHistoryMessage,
    ResponseSubscribePoint,
)


class WebsocketManager:
    def __init__(self):
        self._clients_by_client_id: Dict[UUID, WebsocketClient] = {}
        self._clients_by_asset_id: Dict[int, List[WebsocketClient]] = {}

    async def add_client(self, websocket: WebSocket) -> UUID:
        """Add a client and return client_id."""

        client = WebsocketClient(websocket=websocket)
        self._clients_by_client_id[client.client_id] = client

        # Accept websocket connection
        await client.websocket.accept()

        return client.client_id

    def remove_client(self, client_id: UUID):
        """Remove a client."""

        client: WebsocketClient = self._clients_by_client_id.pop(client_id)

        if client.is_subscribed and client.asset_id:
            self._clients_by_asset_id[client.asset_id].remove(client)

    def add_subscription(self, client_id: UUID, asset_id: int):
        """Add a subscription for asset points."""

        client = self._clients_by_client_id[client_id]

        # If this client is already subscribed, unsubscribe
        if client.is_subscribed and client.asset_id:
            self._clients_by_asset_id[client.asset_id].remove(client)

        client.is_subscribed = True
        client.asset_id = asset_id

        if asset_id in self._clients_by_asset_id:
            self._clients_by_asset_id[asset_id].append(client)
        else:
            self._clients_by_asset_id[asset_id] = [client]

    async def send_error(self, client_id: UUID, error_type: str, error_text: str):
        """Return an error to a client."""

        await self._clients_by_client_id[client_id].websocket.send_json(
            ResponseError(
                message=ResponseErrorMessage(
                    error_type=error_type, error_text=error_text
                )
            ).dict()
        )

    async def send_assets(self, client_id: UUID, assets: List[Asset]):
        """Send a list of assets to the client."""

        await self._clients_by_client_id[client_id].websocket.send_json(
            ResponseAssets(message=ResponseAssetsMessage(assets=assets)).dict()
        )

    async def send_asset_history(
        self, client_id: UUID, asset_history: List[AssetPoint]
    ):
        """Send asset history to a client."""

        await self._clients_by_client_id[client_id].websocket.send_json(
            ResponseSubscribeHistory(
                message=ResponseSubscribeHistoryMessage(points=asset_history)
            ).dict()
        )

    async def broadcast_asset_points(self, asset_points: List[AssetPoint]):
        """Broadcast asset points to all subscribed clients."""

        broadcasts: list = []

        for asset_point in asset_points:
            if asset_point.assetId in self._clients_by_asset_id:
                for client in self._clients_by_asset_id[asset_point.assetId]:
                    broadcasts.append(
                        client.websocket.send_json(
                            ResponseSubscribePoint(message=asset_point).dict()
                        )
                    )

        # Blocking is not a problem, since each `broadcast_asset_points`
        # is started in a new task.
        await asyncio.gather(*broadcasts)
