# Copyright 2020 Planet Labs, Inc.
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
'''Manage authentication with Planet APIs'''
from __future__ import annotations  # https://stackoverflow.com/a/33533514
import abc
import json
import logging
import os

import httpx

ENV_API_KEY = 'PL_API_KEY'

SECRET_FILE_PATH = os.path.join(os.path.expanduser('~'), '.planet.json')

LOGGER = logging.getLogger(__name__)


class AuthException(Exception):
    '''exceptions thrown by Auth'''
    pass


class Auth(metaclass=abc.ABCMeta):
    '''Handle authentication information for use with Planet APIs.'''
    @staticmethod
    def read(
        key: str = None
    ) -> APIKeyAuth:
        '''Reads authentication information.

        If key is provided, uses the key. Otherwise, tries to find key from
        environment variable `PL_API_KEY`. Finally, tries to find key from the
        planet secret file, named `.planet.json` and stored in the user
        directory.

        Parameters:
            key: Planet API key
        '''
        if key:
            auth = Auth.from_key(key)
        else:
            try:
                auth = Auth.from_env(ENV_API_KEY)
            except AuthException:
                try:
                    auth = Auth.from_file(SECRET_FILE_PATH)
                except FileNotFoundError:
                    raise AuthException(
                        'Could not find authentication information. Set '
                        f'environment variable {ENV_API_KEY} or store '
                        'information in secret file with `Auth.write()`')
        return auth

    @staticmethod
    def from_key(
        key: str
    ) -> Auth:
        '''Obtain authentication from api key.

        Parameters:
            key: Planet API key
        '''
        auth = APIKeyAuth(key=key)
        LOGGER.debug('Auth obtained from api key.')
        return auth

    @staticmethod
    def from_file(
        filename: str = None
    ) -> Auth:
        '''Create authentication from secret file.

        The secret file is named `.planet.json` and is stored in the user
        directory. The file has a special format and should have been created
        with `Auth.write()`.

        Parameters:
            filename: Alternate path for the planet secret file.

        '''
        filename = filename or SECRET_FILE_PATH

        try:
            secrets = _SecretFile(filename).read()
            auth = APIKeyAuth.from_dict(secrets)
        except FileNotFoundError:
            raise AuthException(f'File {filename} does not exist.')
        except KeyError:
            raise AuthException(f'File {filename} is not the correct format.')

        LOGGER.debug(f'Auth read from secret file {filename}.')
        return auth

    @staticmethod
    def from_env(
        variable_name: str = None
    ) -> Auth:
        '''Create authentication from environment variable.

        Reads the `PL_API_KEY` environment variable

        Parameters:
            variable_name: Alternate environment variable.
        '''
        variable_name = variable_name or ENV_API_KEY
        api_key = os.getenv(variable_name)
        try:
            auth = APIKeyAuth(api_key)
            LOGGER.info(f'Auth set from environment variable {variable_name}')
        except APIKeyAuthException:
            raise AuthException(
                f'Environment variable {variable_name} either does not exist '
                'or is empty.')
        return auth

    @classmethod
    @abc.abstractmethod
    def from_dict(
        cls,
        data: dict
    ) -> Auth:
        pass

    def write(
        self,
        filename: str = None
    ):
        '''Write authentication information.

        Parameters:
            filename: Alternate path for the planet secret file.
        '''
        filename = filename or SECRET_FILE_PATH
        secret_file = _SecretFile(filename)
        secret_file.write(self.to_dict())


class APIKeyAuthException(Exception):
    '''exceptions thrown by APIKeyAuth'''
    pass


class APIKeyAuth(httpx.BasicAuth, Auth):
    '''Planet API Key authentication.'''
    DICT_KEY = 'key'

    def __init__(
        self,
        key: str
    ):
        '''Initialize APIKeyAuth.

        Parameters:
            key: API key.

        Raises:
            APIKeyException: If API key is None or empty string.
        '''
        if not key:
            raise APIKeyAuthException('API key cannot be empty.')
        self.key = key
        super().__init__(self.key, '')

    @classmethod
    def from_dict(
        cls,
        data: dict
    ) -> APIKeyAuth:
        '''Instantiate APIKeyAuth from a dict.'''
        api_key = data[cls.DICT_KEY]
        return cls(api_key)

    def to_dict(self):
        '''Represent APIKeyAuth as a dict.'''
        return {self.DICT_KEY: self.key}


class _SecretFile():
    def __init__(self, path):
        self.path = path

    def write(
        self,
        contents: dict
    ):
        try:
            secrets_to_write = self.read()
            secrets_to_write.update(contents)
        except FileNotFoundError:
            secrets_to_write = contents

        self._write(secrets_to_write)

    def _write(
        self,
        contents: dict
    ):
        LOGGER.debug(f'Writing to {self.path}')
        with open(self.path, 'w') as fp:
            fp.write(json.dumps(contents))

    def read(self) -> dict:
        LOGGER.debug(f'Reading from {self.path}')
        with open(self.path, 'r') as fp:
            contents = json.loads(fp.read())
        return contents
