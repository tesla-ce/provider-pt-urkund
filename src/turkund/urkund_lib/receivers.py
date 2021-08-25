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
""" Receivers module """
import json
import urllib


class Receivers:
    """
    Receivers class
    """
    _unit = None
    _organization = None
    _sub_organization = None
    _suffix = None

    def __init__(self, config, request):
        self._unit = config['unit']
        self._organization = config['organization']
        self._sub_organization = config['sub_organization']
        self._request = request
        self._suffix = config['suffix']

    def get_suffix(self):
        """
        Get suffix
        :return:
        """
        return self._suffix

    def create(self, full_name, email):
        """
        Create receiver
        :param full_name:
        :param email:
        :return:
        """
        receiver = {
            "UnitId": self._unit,
            "FullName": full_name,
            "EmailAddress": email
        }
        if self._organization is not None:
            receiver['OrganizationId'] = self._organization

        if self._organization is not None:
            receiver['SubOrganizationId'] = self._sub_organization

        data = json.dumps(receiver)

        headers_send = {'Content-Type': 'application/json'}

        return self._request.make(verb='POST', url='receivers', data=data, headers=headers_send)

    def update(self, full_name, email):
        """
        Update receiver
        :param full_name:
        :param email:
        :return:
        """
        receiver = {
            "UnitId": self._unit,
            "FullName": full_name,
            "EmailAddress": email,
            "OrganizationId": self._organization,
            "SubOrganizationId": self._sub_organization,
        }

        data = json.dumps(receiver)

        headers_send = {'Content-Type': 'application/json'}

        return self._request.make(verb='PUT', url='receivers', data=data, headers=headers_send)

    def delete(self, analysis_email):
        """
        Delete receiver
        :param analysis_email:
        :return:
        """
        email_url_encoded = urllib.parse.quote(analysis_email)

        return self._request.make('DELETE', 'receivers/'+str(email_url_encoded))

    def get_by_email(self, email):
        """
        Ger receiver by email
        :param email:
        :return:
        """
        first_part = email.split('@')[0]

        analysis_email = str(first_part)+str(self._suffix)

        return self.get(analysis_email=analysis_email)

    def get(self, analysis_email):
        """
        Get receiver by analysis email
        :param analysis_email:
        :return:
        """
        email_url_encoded = urllib.parse.quote(analysis_email)

        return self._request.make('GET', 'receivers/'+str(email_url_encoded))

    def get_all(self):
        """
        Get all receivers
        :return:
        """
        return self._request.make('GET', 'receivers')
