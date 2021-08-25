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
""" Units module """


class Units:
    """
    Units class
    """
    unit = None
    organization = None
    request = None

    def __init__(self, request):
        self.request = request

    def get(self, unit_id):
        """
        Get unit
        :param unit_id:
        :return:
        """
        return self.request.make(verb='GET', url='units/'+str(unit_id))

    def get_organizations(self, unit_id):
        """
        Get organizations of unit
        :param unit_id:
        :return:
        """
        return self.request.make(verb='GET', url='units/'+str(unit_id)+"/organizations")

    def get_all(self):
        """
        Get all units
        :return:
        """
        return self.request.make(verb='GET', url='units')
