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
from unittest.mock import MagicMock

import planet


def test__BaseClient_init():
    session = MagicMock(spec=planet.Session)

    cl = planet.clients._base._BaseClient(session)
    assert cl.base_url == planet.constants.PLANET_BASE_URL

    base_url = 'base/url'
    cl = planet.clients._base._BaseClient(session, base_url)
    assert cl.base_url == 'base/url/'
