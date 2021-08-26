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
""" UrkundLib module """
from .exceptions import UnitAndOrganizationNotValid
from .receivers import Receivers
from .request import Request
from .submissions import Submissions
from .units import Units


class UrkundLib:
    """
        UrkundLib class
    """
    _base_url = None
    _config = {
        'base_url': None,
        'user': None,
        'password': None,
        'unit': None,
        'organization': None,
        'sub_organization': None,
        'suffix': None,
        'valid_unit_and_organization': False
    }
    _request = None
    _receivers = None
    _submissions = None
    _units = None

    def __init__(self, user, password, **kwargs):
        self._config['base_url'] = 'https://secure.urkund.com/api/'
        self._config['user'] = user
        self._config['password'] = password

        unit = None
        if 'unit' in kwargs.keys():
            unit = kwargs['unit']
        self._config['unit'] = int(unit)

        organization = None
        if 'organization' in kwargs.keys():
            organization = kwargs['organization']

        if organization is not None:
            self._config['organization'] = int(organization)

        sub_organization = None
        if 'sub_organization' in kwargs.keys():
            sub_organization = kwargs['sub_organization']

        if sub_organization is not None:
            self._config['sub_organization'] = int(sub_organization)

        self._config['valid_unit_and_organization'] = False
        self._config['suffix'] = None

        self.request = Request(base_url=self._config['base_url'], user=self._config['user'],
                               password=self._config['password'])
        self._units = Units(request=self.request)
        self._submissions = Submissions(organization=self._config['organization'], request=self.request)
        self.init()

    def init(self):
        """
        Check if variables are correct: user, password, unit, organization, sub_organization
        :return:
        """
        # check if the user and password provided are correct
        if self._config['valid_unit_and_organization'] is True:
            return

        unit = self.units.get(self._config['unit'])

        self._config['valid_unit_and_organization'] = False
        valid_unit = False
        valid_organization = False
        valid_sub_organization = False
        organization = None
        if unit is not None and unit['Id'] == self._config['unit']:
            self._config['suffix'] = unit['Suffix']
            valid_unit = True

        # check if unit and organization provided are correct
        if valid_unit and self._config['organization'] is not None:
            for organization in unit['Organizations']:
                if organization['Id'] == self._config['organization']:
                    valid_organization = True
                    break

        if valid_organization and self._config['sub_organization'] is not None:
            for sorg in organization['SubOrganizations']:
                if sorg['Id'] == self._config['sub_organization']:
                    valid_sub_organization = True
                    break

        if (valid_unit and valid_organization and valid_sub_organization) or \
                (valid_unit and valid_organization and self._config['sub_organization'] is None) or \
                (valid_unit and self._config['organization'] is None):
            self._config['valid_unit_and_organization'] = True

        if not self._config['valid_unit_and_organization']:
            raise UnitAndOrganizationNotValid()

        assert self._config['suffix'] is not None
        self._receivers = Receivers(config=self._config, request=self.request)

    @property
    def units(self):
        """
        Return Units property
        :return: Units
        """
        return self._units

    @property
    def receivers(self):
        """
        Return Receivers property
        :return: Receivers
        """
        return self._receivers

    @property
    def submissions(self):
        """
        Return Submissions property
        :return: Submissions
        """
        return self._submissions


__all__ = [
    'UrkundLib',
    'exceptions'
]
