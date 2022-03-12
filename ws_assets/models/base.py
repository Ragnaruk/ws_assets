from pydantic import BaseModel, Extra


class BaseClass(BaseModel):
    class Config:
        # # Change default json encoders/decoders to orjson ones
        # json_loads = orjson.loads
        # json_dumps = orjson_dumps

        # Don't allow extra fields
        extra = Extra.forbid
