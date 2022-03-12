from typing import List, Literal

from pydantic import Field

from ws_assets.models.asset import Asset, AssetPoint
from ws_assets.models.base import BaseClass


# "error"
class ResponseErrorMessage(BaseClass):
    error_type: str = Field(description="Error type.")
    error_text: str = Field(description="Error message.")


class ResponseError(BaseClass):
    action: Literal["error"] = Field("error", description="Action type.")
    message: ResponseErrorMessage = Field(description="Message object.")


# "assets"
class ResponseAssetsMessage(BaseClass):
    assets: List[Asset] = Field(description="List of assets.")


class ResponseAssets(BaseClass):
    action: Literal["assets"] = Field("assets", description="Action type.")
    message: ResponseAssetsMessage = Field(description="Message object.")


# "subscribe"
class ResponseSubscribeHistoryMessage(BaseClass):
    points: List[AssetPoint] = Field(description="List of asset points.")


class ResponseSubscribeHistory(BaseClass):
    action: Literal["asset_history"] = Field(
        "asset_history", description="Action type."
    )
    message: ResponseSubscribeHistoryMessage = Field(description="Message object.")


class ResponseSubscribePoint(BaseClass):
    action: Literal["point"] = Field("point", description="Action type.")
    message: AssetPoint = Field(description="Message object.")
