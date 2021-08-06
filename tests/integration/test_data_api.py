# Copyright 2021 Planet Labs, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
import copy
from http import HTTPStatus
import logging
from unittest.mock import MagicMock

import httpx
import pytest
import respx

from planet import DataClient, exceptions


TEST_URL = 'http://MockNotRealURL/'

LOGGER = logging.getLogger(__name__)


@pytest.fixture
def feature_descriptions(feature_description):
    feature1 = feature_description
    feature1['id'] = 'oid1'
    feature2 = copy.deepcopy(feature_description)
    feature2['id'] = 'oid2'
    feature3 = copy.deepcopy(feature_description)
    feature3['id'] = 'oid3'
    return [feature1, feature2, feature3]


@respx.mock
@pytest.mark.asyncio
async def test_DataClient_quick_search(feature_descriptions, session):
    search_url = TEST_URL + 'data/v1/quick-search'
    next_page_url = search_url + 'blob/_page=IAmATest'

    feature1, feature2, feature3 = feature_descriptions

    page1_response = {
        "_links": {
            "_self": "string",
            "_next": next_page_url
        },
        "features": [feature1, feature2]
    }
    mock_resp1 = httpx.Response(HTTPStatus.OK, json=page1_response)
    respx.post(search_url).return_value = mock_resp1

    page2_response = {
        "_links": {
            "_self": next_page_url
        },
        "features": [feature3]
    }
    mock_resp2 = httpx.Response(HTTPStatus.OK, json=page2_response)
    respx.post(next_page_url).return_value = mock_resp2

    cloud_filter = {
        'config': {'lt': 0.2},
        'field_name': 'cloud_cover',
        'type': 'RangeFilter'
    }
    item_types = ['Landsat8L1G']

    cl = DataClient(session, base_url=TEST_URL)
    items = await cl.quick_search(cloud_filter, item_types)

    iids = list(i.id for i in items)
    assert iids == ['oid1', 'oid2', 'oid3']


@respx.mock
@pytest.mark.asyncio
async def test_DataClient_quick_search_bad_item_type(
        feature_description, session, match_pytest_raises):
    search_url = (TEST_URL + 'data/v1/quick-search')

    msg = "Not all item types requested exist or are accessible"
    resp = {
        "general": [],
        "field": {
            "item_types": [
                {
                    "message": msg
                }
            ]
        }
    }
    mock_resp = httpx.Response(400, json=resp)
    respx.post(search_url).return_value = mock_resp

    cloud_filter = {
        'config': {'lt': 0.2},
        'field_name': 'cloud_cover',
        'type': 'RangeFilter'
    }
    item_types = ['InvalidItemType']

    cl = DataClient(session, base_url=TEST_URL)

    with match_pytest_raises(exceptions.BadQuery, msg):
        _ = await cl.quick_search(cloud_filter, item_types)


@respx.mock
@pytest.mark.asyncio
async def test_DataClient_get_assets(session):
    item = MagicMock()
    item.type = 'itemtype'
    item.id = 'itemid'

    assets_url = TEST_URL + 'data/v1/item-types/itemtype/items/itemid'

    assets = {
        "analytic": {
            "_links": {
                "_self": "selfurl",
                "activate": "activateurl",
                "type": "https://api.planet.com/data/v1/asset-types/analytic"
            },
            "_permissions": ["download"],
            "expires_at": "2021-08-06T01:03:31.182143",
            "location": "downloadurl",
            "md5_digest": "1fb0e331c05a52d5eb847d6fc018320d",
            "status": "active",
            "type": "analytic"
        },
        "analytic_5b": {
            "_links": {
                "_self": "selfurl",
                "activate": "activateurl",
                "type": "https://api.planet.com/data/v1/asset-types/analytic_5b" # noqa
            },
            "_permissions": ["download"],
            "md5_digest": None,
            "status": "inactive",
            "type": "analytic_5b"
          }
    }
    mock_resp = httpx.Response(HTTPStatus.OK, json=assets)
    respx.get(assets_url).return_value = mock_resp

    cl = DataClient(session, base_url=TEST_URL)
    assets = await cl.get_assets(item)

    assert assets[0].status == 'active'
    assert assets[1].status == 'inactive'


@respx.mock
@pytest.mark.asyncio
async def test_DataClient_get_assets_bad_type(session, match_pytest_raises):
    item = MagicMock()
    item.type = 'baditemtype'
    item.id = 'itemid'

    assets_url = TEST_URL + 'data/v1/item-types/baditemtype/items/itemid'

    msg = "The requested item type does not exist."
    resp = {
        "general": [
            {
                "message": msg
            }
        ],
        "field": {}
    }
    mock_resp = httpx.Response(404, json=resp)
    respx.get(assets_url).return_value = mock_resp

    cl = DataClient(session, base_url=TEST_URL)

    with match_pytest_raises(exceptions.MissingResource, msg):
        _ = await cl.get_assets(item)


@respx.mock
@pytest.mark.asyncio
async def test_DataClient_get_assets_bad_id(session, match_pytest_raises):
    item = MagicMock()
    item.type = 'itemtype'
    item.id = 'baditemid'

    assets_url = TEST_URL + 'data/v1/item-types/itemtype/items/baditemid'

    msg = "Could not find the requested item."
    resp = {
        "general": [
            {
                "message": msg
            }
        ],
        "field": {}
    }
    mock_resp = httpx.Response(404, json=resp)
    respx.get(assets_url).return_value = mock_resp

    cl = DataClient(session, base_url=TEST_URL)

    with match_pytest_raises(exceptions.MissingResource, msg):
        _ = await cl.get_assets(item)
