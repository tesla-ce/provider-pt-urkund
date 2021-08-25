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
""" Exceptions module """
from .bad_request import BadRequest
from .base_urkund_lib_exception import BaseUrkundLibException
from .invalid_response import InvalidResponse
from .media_type_not_supported import MediaTypeNotSupported
from .mime_type_not_supported import MimeTypeNotSupported
from .receiver_exists import ReceiverExists
from .not_found import NotFound
from .request_too_large import RequestTooLarge
from .submission_not_found import SubmissionNotFound
from .unauthorized import Unauthorized
from .unit_and_organization_not_valid import UnitAndOrganizationNotValid
from .not_available import NotAvailable
from .timeout import Timeout
