from datetime import datetime

from pydantic import Field, validator

from ws_assets.models.base import BaseClass


class Asset(BaseClass):
    id: int = Field(description="Unique asset ID.")
    name: str = Field(description="Asset name.")


class AssetPoint(BaseClass):
    assetName: str = Field(description="Asset name.")
    time: int = Field(description="Point timestamp.")
    assetId: int = Field(description="Asset ID.")
    value: float = Field(description="Asset value.")

    @validator("time", pre=True)
    def timestamp(cls, v, values, **kwargs):
        if isinstance(v, datetime):
            return v.timestamp()

        return v
