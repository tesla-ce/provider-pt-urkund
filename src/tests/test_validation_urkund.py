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
""" TeSLA CE TFR validation tests module """
from .utils import get_request


def test_send_zip_filename(mock_urkund_lib_all_ok, urkund_provider):
    filename = 'valid/lorem.txt.zip'
    sample = get_request(filename=filename, mimetype='application/zip')

    model = {}
    response = urkund_provider.verify(sample, model)

    from tesla_provider import result
    assert isinstance(response, result.VerificationDelayedResult)


def test_send_zip_filename(mock_urkund_lib_all_ok, urkund_provider):
    filename = 'valid/lorem.txt.zip'
    sample = get_request(filename=filename, mimetype='application/zip')

    model = {}
    response = urkund_provider.verify(sample, model)

    from tesla_ce_provider import result
    assert isinstance(response, result.VerificationDelayedResult)


def test_send_txt_filename(mock_urkund_lib_all_ok, urkund_provider):
    filename = 'valid/lorem.txt'
    sample = get_request(filename=filename, mimetype='text/plain')

    model = {}
    response = urkund_provider.verify(sample, model)

    from tesla_ce_provider import result
    assert isinstance(response, result.VerificationDelayedResult)


def test_verify_txt_filename(mock_urkund_lib_all_ok, urkund_provider):
    key = 'tukrund_check_data'
    info = {
        'request_id': '',
        'learner_id': '',
        'external_ids': [{
            'external_id': '1610712121.915711_0',
            'analysis_email': 'rmunozber.uoc@analysis.urkund.com',
            'filename': 'lorem.txt'
        }],
        'processed_external_ids': {
            'errors': [],
            'corrects': []
        },
        'errors': [],
        'countdown': 5,
        'total_files': 1
    }

    result = urkund_provider.on_notification(key, info)

    assert result is None
