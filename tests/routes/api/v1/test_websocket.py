import asyncio

from fastapi.testclient import TestClient


async def test_websocket_incorrect_not_dict(client: TestClient):
    with client.websocket_connect("/api/v1/websocket") as websocket:
        websocket.send_json(123)

        data: dict = websocket.receive_json()

        assert data == {
            "action": "error",
            "message": {
                "error_type": "RequestParsingError",
                "error_text": "Failed to parse request data. Expected type: `dict`, received type: `int`",
            },
        }


async def test_websocket_incorrect_wrong_action(client: TestClient):
    with client.websocket_connect("/api/v1/websocket") as websocket:
        websocket.send_json({"action": "test_action", "message": {}})

        data: dict = websocket.receive_json()

        assert data == {
            "action": "error",
            "message": {
                "error_type": "ValidationError",
                "error_text": "1 validation error for GenericRequest\naction\n  unexpected value; permitted: 'assets', 'subscribe' (type=value_error.const; given=test_action; permitted=('assets', 'subscribe'))",
            },
        }


async def test_websocket_close(client: TestClient):
    with client.websocket_connect("/api/v1/websocket") as websocket:
        websocket.send_json({"action": "assets", "message": {}})
        websocket.close()

    await asyncio.sleep(1)


async def test_websocket_assets(client: TestClient):
    with client.websocket_connect("/api/v1/websocket") as websocket:
        websocket.send_json({"action": "assets", "message": {}})

        data: dict = websocket.receive_json()

        assert data == {
            "action": "assets",
            "message": {
                "assets": [
                    {"id": 1, "name": "EURUSD"},
                    {"id": 2, "name": "USDJPY"},
                    {"id": 3, "name": "GBPUSD"},
                    {"id": 4, "name": "AUDUSD"},
                    {"id": 5, "name": "USDCAD"},
                ]
            },
        }


async def test_websocket_subscribe(client: TestClient):
    with client.websocket_connect("/api/v1/websocket") as websocket:
        websocket.send_json({"action": "subscribe", "message": {"assetId": 1}})

        data: dict = websocket.receive_json()

        assert data == {
            "action": "asset_history",
            "message": {
                "points": [
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
            },
        }

        await asyncio.sleep(2)

        data = websocket.receive_json()

        assert data == {
            "action": "point",
            "message": {
                "assetName": "EURUSD",
                "time": 1647092464,
                "assetId": 1,
                "value": 1.0911849999999998,
            },
        }
