import asyncio
import random
from datetime import datetime
from typing import AsyncGenerator, List

from fastapi import FastAPI
from pytest_asyncio import fixture
from starlette.testclient import TestClient

from ws_assets.main import create_app
from ws_assets.tools.asset_processor import AssetProcessor
from ws_assets.tools.mocks.mock_asset_processor import MockAssetProcessor
from ws_assets.tools.mocks.mock_db_client import MockDBClient


def get_fetchall_assets() -> List[dict]:
    return [
        {"id": 1, "name": "EURUSD"},
        {"id": 2, "name": "USDJPY"},
    ]


def get_fetchall_asset_points() -> List[dict]:
    return [
        {
            "assetName": "EURUSD",
            "time": datetime.utcnow(),
            "assetId": 1,
            "value": random.random(),
        },
        {
            "assetName": "EURUSD",
            "time": datetime.utcnow(),
            "assetId": 1,
            "value": random.random(),
        },
    ]


def get_fetchall_asset_points_without_asset_name() -> List[dict]:
    return [
        {
            "time": datetime.utcnow(),
            "assetId": 1,
            "value": random.random(),
        }
    ]


def get_response_text() -> str:
    return """null({"Rates":[{"Symbol":"EURUSD","Bid":"1.09107","Ask":"1.0913","Spread":"2.30","ProductType":"1",},{"Symbol":"COIN.us","Bid":"160.15","Ask":"160.27","Spread":"12.00","ProductType":"8",},{"Symbol":"USOil","Bid":"109.14","Ask":"109.18","Spread":"4.00","ProductType":"3",},{"Symbol":"FVRR.us","Bid":"63.29","Ask":"63.42","Spread":"13.00","ProductType":"8",},{"Symbol":"AUDCAD","Bid":"0.92935","Ask":"0.9302","Spread":"8.50","ProductType":"1",},{"Symbol":"US.ECOMM","Bid":"1806.63","Ask":"1808.02","Spread":"1.39","ProductType":"8",},{"Symbol":"TRAVEL","Bid":"3240.76","Ask":"3249.16","Spread":"8.40","ProductType":"8",}]}); """


def get_mock_db_client(return_fetchall: List[dict] = None) -> MockDBClient:
    return MockDBClient(return_fetchall=return_fetchall)


def get_asset_processor(return_fetchall: List[dict] = None) -> AssetProcessor:
    db_client: MockDBClient = get_mock_db_client(return_fetchall=return_fetchall)

    asset_processor = AssetProcessor(
        dsn=None,  # type: ignore
        http_client=None,  # type: ignore
        db_client=db_client,  # type: ignore
        subscription_handler=None,  # type: ignore
    )

    async def mock_make_request_to_asset_endpoint() -> str:
        return get_response_text()

    asset_processor._make_request_to_asset_endpoint = (  # type: ignore
        mock_make_request_to_asset_endpoint
    )

    return asset_processor


@fixture(scope="function")
async def client() -> AsyncGenerator:
    """FastAPI test client."""

    app = create_app()

    app.state.DBClient = get_mock_db_client()

    app.state.AssetProcessor = MockAssetProcessor(
        subscription_handler=app.state.WebsocketManager.broadcast_asset_points
    )
    task = asyncio.create_task(app.state.AssetProcessor.start_receiving_asset_points())

    client = TestClient(app)
    yield client

    task.cancel()
    await app.state.ClientSession.close()
