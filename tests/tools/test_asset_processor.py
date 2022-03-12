import json
from typing import Dict, List

import pytest

from tests.conftest import (
    get_asset_processor,
    get_fetchall_asset_points,
    get_fetchall_asset_points_without_asset_name,
    get_fetchall_assets,
    get_response_text,
)
from ws_assets.exceptions import UnknownAssetIDError
from ws_assets.models.asset import Asset, AssetPoint
from ws_assets.tools.asset_processor import AssetProcessor


async def test_fetch_assets():
    return_fetchall: List[dict] = get_fetchall_assets()
    asset_processor: AssetProcessor = get_asset_processor(
        return_fetchall=return_fetchall
    )

    assets: List[Asset] = await asset_processor.fetch_assets()

    assert all([isinstance(asset, Asset) for asset in assets])
    assert (
        len(assets)
        == len(return_fetchall)
        == len(asset_processor._assets_name_to_id)
        == len(asset_processor._assets_id_to_name)
    )


async def test_fetch_asset_history_correct():
    return_fetchall: List[dict] = get_fetchall_asset_points()
    asset_processor: AssetProcessor = get_asset_processor(
        return_fetchall=return_fetchall
    )

    asset_processor._assets_id_to_name = {1: "EURUSD"}
    asset_history: List[AssetPoint] = await asset_processor.fetch_asset_history(
        asset_id=1
    )

    assert all([isinstance(asset_point, AssetPoint) for asset_point in asset_history])
    assert len(asset_history) == len(return_fetchall)


async def test_fetch_asset_history_incorrect_asset_id():
    return_fetchall: List[dict] = get_fetchall_asset_points()
    asset_processor: AssetProcessor = get_asset_processor(
        return_fetchall=return_fetchall
    )

    asset_processor._assets_id_to_name = {2: "USDJPY"}

    with pytest.raises(UnknownAssetIDError):
        await asset_processor.fetch_asset_history(asset_id=1)


async def test_parse_asset_text():
    text: str = get_response_text()
    asset_processor: AssetProcessor = get_asset_processor()

    asset_points: Dict[str, List[dict]] = asset_processor._parse_asset_text(text=text)

    assert isinstance(asset_points, dict)
    assert "Rates" in asset_points
    assert isinstance(asset_points["Rates"], list)


async def test_filter_unused_assets():
    text: str = get_response_text()
    asset_processor: AssetProcessor = get_asset_processor()
    asset_processor._assets_id_to_name = {1: "EURUSD"}
    asset_processor._assets_name_to_id = {"EURUSD": 1}

    asset_points: Dict[str, List[dict]] = asset_processor._parse_asset_text(text=text)
    useful_asset_points: List[dict] = asset_processor._filter_unused_assets(
        asset_points=asset_points
    )

    assert isinstance(useful_asset_points, list)
    assert len(useful_asset_points) == 1
    assert useful_asset_points[0] == json.loads(
        '{"Symbol":"EURUSD","Bid":"1.09107","Ask":"1.0913","Spread":"2.30","ProductType":"1"}'
    )


async def test_receive_asset_point():
    return_fetchall: List[dict] = get_fetchall_asset_points_without_asset_name()
    asset_processor: AssetProcessor = get_asset_processor(
        return_fetchall=return_fetchall
    )
    asset_processor._assets_id_to_name = {1: "EURUSD"}
    asset_processor._assets_name_to_id = {"EURUSD": 1}

    results: List[AssetPoint] = []

    async def mock_subscription_handler(asset_points: List[AssetPoint]):
        results.extend(asset_points)

    asset_processor._subscription_handler = mock_subscription_handler

    await asset_processor._receive_asset_point()

    assert len(results) == 1
