#  Copyright (c) 2020 Roger Muñoz Bernaus
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
""" Request module """
import base64
import json
import requests
from requests.exceptions import Timeout
from .exceptions import Unauthorized
from .exceptions import Timeout as RequestTimeout
from .exceptions import BadRequest
from .exceptions import InvalidResponse
from .exceptions import NotFound
from .exceptions import NotAvailable
from .exceptions import MediaTypeNotSupported
from .exceptions import ReceiverExists
from .exceptions import RequestTooLarge


class Request:
    """
    Request class
    """
    _base_url = None
    _user = None
    _password = None
    _hash_user_password = None
    """
    Request class
    """
    def __init__(self, base_url, user, password):
        self._base_url = base_url
        self._user = user
        self._password = password

        user_password = str(self._user)+':'+str(self._password)
        self._hash_user_password = base64.b64encode(user_password.encode()).decode('utf-8')

    def make(self, verb, url, data=None, headers=None):
        """
        Make HTTP request
        :param verb:
        :param url:
        :param data:
        :param headers:
        :return:
        """
        if headers is None:
            headers = {}

        headers_send = headers
        headers_send['Authorization'] = 'Basic '+str(self._hash_user_password)
        headers_send['Accept'] = 'application/json'

        headers_send['Accept-Language'] = 'en-US'
        headers_send['Content-Language'] = 'en-US'

        try:
            response = requests.request(method=verb, url=self._base_url+url, headers=headers_send, data=data,
                                        timeout=20)
            return self._process_response(response)
        except Timeout as timeout:
            raise RequestTimeout() from timeout

    @staticmethod
    def _process_response(response):
        """
        Process HTTP Urkund response
        :param response:
        :return:
        """
        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))

        if response.status_code == 202:
            return json.loads(response.content.decode('utf-8'))

        if response.status_code == 400:
            raise BadRequest(response.content.decode('utf-8'))

        if response.status_code == 401:
            raise Unauthorized()

        if response.status_code == 404:
            raise NotFound(response.content.decode('utf-8'))

        if response.status_code == 409:
            raise ReceiverExists()

        if response.status_code == 410:
            raise NotAvailable(response.content.decode('utf-8'))

        if response.status_code == 415:
            raise MediaTypeNotSupported(response.content.decode('utf-8'))

        if response.status_code == 413:
            raise RequestTooLarge(response.content.decode('utf-8'))

        raise InvalidResponse(response.content.decode('utf-8'))

    def __str__(self):
        return self._base_url+", user"+self._user
