from typing import List
from uuid import UUID

from fastapi import APIRouter
from loguru import logger
from starlette.websockets import WebSocket, WebSocketDisconnect

from ws_assets.exceptions import RequestParsingError
from ws_assets.models.asset import Asset, AssetPoint
from ws_assets.models.request import GenericRequest, RequestAssets, RequestSubscribe
from ws_assets.tools.asset_processor import AssetProcessor
from ws_assets.tools.websocket_manager import WebsocketManager

router = APIRouter(tags=["Websocket"])


@router.websocket("/websocket")
async def websocket_endpoint(websocket: WebSocket):
    websocket_manager: WebsocketManager = websocket.app.state.WebsocketManager
    asset_processor: AssetProcessor = websocket.app.state.AssetProcessor

    client_id: UUID = await websocket_manager.add_client(websocket=websocket)

    while True:
        try:
            raw_data: dict = await websocket.receive_json()

            # Parse request
            if not isinstance(raw_data, dict):
                raise RequestParsingError(request_type=type(raw_data).__name__)

            data: GenericRequest = GenericRequest(**raw_data)

            # Handle request logic
            if data.action == "assets":
                request_assets: RequestAssets = RequestAssets(**data.dict())

                assets: List[Asset] = await asset_processor.fetch_assets()
                await websocket_manager.send_assets(client_id=client_id, assets=assets)
            elif data.action == "subscribe":
                request_subscribe: RequestSubscribe = RequestSubscribe(**data.dict())

                asset_history: List[
                    AssetPoint
                ] = await asset_processor.fetch_asset_history(
                    asset_id=request_subscribe.message.assetId
                )
                await websocket_manager.send_asset_history(
                    client_id=client_id, asset_history=asset_history
                )

                websocket_manager.add_subscription(
                    client_id=client_id, asset_id=request_subscribe.message.assetId
                )
        except WebSocketDisconnect:
            websocket_manager.remove_client(client_id=client_id)

            break
        except Exception as e:
            logger.exception(e)
            await websocket_manager.send_error(
                client_id=client_id, error_type=type(e).__name__, error_text=str(e)
            )
