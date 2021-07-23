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
"""Base functionality for interacting with the planet apis"""
import logging

from .. import constants, http, models

LOGGER = logging.getLogger(__name__)

BASE_URL = constants.PLANET_BASE_URL


class _BaseClient():
    """Base functionality for high-level asynchronous access to Planet's API's.
    """
    def __init__(
        self,
        session: http.Session,
        base_url: str = None
    ):
        """
        Parameters:
            session: Open session connected to server.
            base_url: The base URL to use. Defaults to production orders API
                base url.
        """
        self._session = session

        self._base_url = base_url or BASE_URL
        if not self._base_url.endswith('/'):
            self._base_url += '/'

    @property
    def base_url(self) -> str:
        return self._base_url

    def _request(self, url, method, data=None, params=None, json=None):
        return models.Request(url, method=method, data=data, params=params,
                              json=json)

    async def _do_request(
        self,
        request: models.Request
    ) -> models.Response:
        '''Submit a request and get response.
        Parameters:
            request: request to submit
        '''
        return await self._session.request(request)
