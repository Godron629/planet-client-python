# Copyright 2015 Planet Labs, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from .utils import read_planet_json, write_planet_json
from datetime import datetime
from planet.scripts.oauth import TokenHandler
from calendar import timegm
from planet.scripts.util import get_claim
ENV_KEY = 'PL_API_KEY'

auth_config = {'host': 'account.planet.com',
               'auth_server_id': 'aus2enhwueFYRb50S4x7',
               'client_id': '0oa2scq915nekGLum4x7'}

class APIKey(object):
    def __init__(self, value):
        self.value = value


def find_api_key():
    api_key = os.getenv(ENV_KEY)
    if api_key is None:
        contents = read_planet_json()
        api_key = contents.get('access_token', None)
        expires_on = contents.get('expires_on', None)
        now = timegm(datetime.utcnow().utctimetuple())
        if now > expires_on:
           print("Refreshing the access token....")
           handler = TokenHandler(auth_config)
           tokens = handler.refresh_tokens(contents.get('refresh_token', None))
           expires_on = get_claim(tokens['access_token'], 'exp')
           write_planet_json({'expires_on': expires_on, 'access_token': tokens['access_token'], 'refresh_token': tokens['refresh_token']})
           api_key = tokens['access_token']
    return api_key