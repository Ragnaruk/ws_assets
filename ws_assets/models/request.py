from typing import Literal

from pydantic import Field, validator

from ws_assets.models.base import BaseClass


# generic
class GenericRequest(BaseClass):
    action: Literal["assets", "subscribe"] = Field(description="Action type.")
    message: dict = Field(description="Message object.")


# "assets"
class RequestAssets(BaseClass):
    action: Literal["assets"] = Field(description="Action type.")
    message: dict = Field(description="Empty message object.")

    @validator("message", pre=True)
    def empty_message(cls, v, values, **kwargs):
        if v:
            raise TypeError("Message object should be empty.")
        if not isinstance(v, dict):
            raise TypeError("Message field should be an object.")

        return v


# "subscribe"
class RequestSubscribeMessage(BaseClass):
    assetId: int = Field(description="Asset ID.")


class RequestSubscribe(BaseClass):
    action: Literal["subscribe"] = Field(description="Action type.")
    message: RequestSubscribeMessage = Field(description="Message object.")
