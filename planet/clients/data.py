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
"""Functionality for interacting with the data api"""
import json
import logging
import typing

from ._base import _BaseClient
from .. import exceptions
from ..models import Feature, Features

LOGGER = logging.getLogger(__name__)

DATA_PATH = 'data/v1/'

SORT_ORDER = ['acquired asc', 'acquired desc',
              'published asc', 'published desc']


class DataClient(_BaseClient):
    '''High-level asynchronous access to Planet's Data API.
    Example:
        ```python
        >>> import asyncio
        >>> from planet import Session, DataClient
        >>>
        >>> async def main():
        ...     async with Session() as sess:
        ...         cl = DataClient(sess)
        ...         # use client here
        ...
        >>> asyncio.run(main())
        ```
    '''
    def _data_url(self):
        return self.base_url + DATA_PATH

    async def quick_search(
        self,
        filt: dict,
        item_types: typing.List[str],
        name: str = None,
        page_size: int = None,
        sort: str = None,
        strict: bool = None,
        limit: int = None
    ) -> typing.List[Feature]:
        '''Execute a structured item search.
        Parameters:
            filter: Structured search criteria.
            item_types: The item types to include in the search.
            name: The name of the saved search.
            page_size: Change number of results to return per page from default
                of 250 to given value (which must be less than 250).
            sort: Sort according to custom field and direction, instead of
                'published desc'. Fields are 'acquired' and 'published'.
                Directions are 'asc' and 'desc'.
            strict: Strictly remove false positives from geo intersection.
        '''
        url = self._data_url() + 'quick-search'

        search_body = {
            'filter': filt,
            'item_types': item_types
        }

        async def _request_and_parse(*args, **kwargs):
            try:
                resp = await self._do_request(*args, **kwargs)
            except exceptions.BadQuery as ex:
                msg_json = json.loads(ex.message)

                # get first error field
                field = next(iter(msg_json['field'].keys()))
                msg = msg_json['field'][field][0]['message']
                raise exceptions.BadQuery(msg)
            return resp

        req = self._request(url, method='POST', data=search_body)
        features = Features(req, _request_and_parse, limit=limit)
        return [f async for f in features]
