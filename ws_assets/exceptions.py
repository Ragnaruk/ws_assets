# request
class RequestParsingError(Exception):
    def __init__(self, request_type: str):
        super().__init__(
            f"Failed to parse request data. Expected type: `dict`, received type: `{request_type}`"
        )


# assets
class AssetHTTPRequestError(Exception):
    def __init__(self, code: int, response: str):
        super().__init__(
            f"HTTP request to the asset endpoint ended with code: {code}. Response: {response}"
        )


class AssetParsingError(Exception):
    def __init__(self, text: str):
        super().__init__(f"Failed to parse asset data from: {text}")


class UnknownAssetIDError(Exception):
    def __init__(self, asset_id: int):
        super().__init__(f"Unknown asset ID: {asset_id}")
