from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import Field, validator
from starlette.websockets import WebSocket

from ws_assets.models.base import BaseClass


class WebsocketClient(BaseClass):
    client_id: UUID = Field(description="Client ID.", default_factory=uuid4)
    websocket: Any = Field(description="Client websocket.")
    is_subscribed: bool = Field(False, description="Flag for subscription.")
    asset_id: Optional[int] = Field(description="Asset ID.")

    @validator("websocket", pre=True)
    def websocket_type(cls, v, values, **kwargs):
        if not isinstance(v, WebSocket):
            raise TypeError(f"Unexpected websocket type: {type(v).__name__}")

        return v
