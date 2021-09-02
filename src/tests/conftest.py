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
""" Test fixtures module """
from logging import getLogger
import os
import pytest


@pytest.fixture
def tesla_ce_provider_conf():
    '''
    TeSLACE provider conf fixture
    :return:
    '''
    return {
        'provider_class': 'urkund.UrkundProvider',
        'provider_desc_file': None,
        'instrument': None,
        'info': None
    }


@pytest.fixture
def urkund_provider(tesla_ce_base_provider):
    '''
    Urkund Provider Fixture
    :param tesla_ce_base_provider:
    :return:
    '''
    from urkund import UrkundProvider
    assert isinstance(tesla_ce_base_provider, UrkundProvider)

    logger = getLogger('urkund Tests')
    tesla_ce_base_provider.set_logger(logger.info)

    tesla_ce_base_provider.set_credential('URKUND_USER', os.getenv('URKUND_USER', None))
    tesla_ce_base_provider.set_credential('URKUND_PASSWORD', os.getenv('URKUND_PASSWORD', None))
    tesla_ce_base_provider.set_credential('URKUND_UNIT',os.getenv('URKUND_UNIT', None))
    tesla_ce_base_provider.set_credential('URKUND_ORGANIZATION', os.getenv('URKUND_ORGANIZATION', None))
    tesla_ce_base_provider.set_credential('URKUND_SUBORGANIZATION', os.getenv('URKUND_SUBORGANIZATION', None))
    tesla_ce_base_provider.set_credential('URKUND_DEFAULT_EMAIL_RECEIVER', os.getenv('URKUND_DEFAULT_EMAIL_RECEIVER', 'noreply@tesla-project.eu'))

    return tesla_ce_base_provider


@pytest.fixture
def mock_urkund_lib_all_ok(mocker, urkund_provider):
    """
    Mocker urkund lib all methods ok
    :param mocker:
    :param urkund_provider:
    :return:
    """
    mock_module = {
        'Id': 1,
        'Name': 'TeSLA CE Institution Test',
        'Suffix': '.uoc@analysis.urkund.com',
        'DateCreated': '12/18/2021 11:54:00 AM',
        'Organizations': [
            {'Id': 1, 'Name': "TeSLA CE Test", 'SubOrganizations': []}
        ],
        'MOCKED': True
    }
    mocker.patch('urkund.urkund_lib.units.Units.get', return_value=mock_module)

    mock_module = {
        'Id': 414194,
        'AnalysisAddress': 'rmunozber.uoc@analysis.urkund.com',
        'EmailAddress': 'rmunozber@uoc.edu',
        'FullName': 'Roger John Doe',
        'Language': 'EN ',
        'UnitId': 1,
        'Organization': {'Id': 1, 'Name': 'Estudis', 'SubOrganizations': None},
        'SubOrganization': None,
        'MOCKED': True
    }

    mocker.patch('urkund.urkund_lib.receivers.Receivers.get', return_value=mock_module)

    mock_module = {
        'Id': 72565518,
        'ExternalId': '1610712121.915711_0',
        'Filename': 'lorem.txt',
        'MimeType': 'text/plain',
        'Timestamp': '2021-01-15T12:03:06',
        'Status': {'State': 'Submitted', 'ErrorCode': 0, 'Message': 'The document has been sent to URKUND.'},
        'Document': None,
        'Report': None,
        'Subject': '',
        'Message': '',
        'Anonymous': None,
        'AutoDeleteDocument': False,
        'MOCKED': True
    }

    mocker.patch('urkund.urkund_lib.submissions.Submissions.send', return_value=mock_module)

    mock_module = [{
        'Id': 72565518,
        'ExternalId': '1610712121.915711_0',
        'Filename': 'lorem.txt',
        'MimeType': 'text/plain',
        'Timestamp': '2021-01-15T12:03:06',
        'Status': {
            'State': 'Analyzed',
            'ErrorCode': 0,
            'Message': 'The document has been analyzed.'
        },
        'Document': {
            'Id': 92305055,
            'Date': '2021-01-15T12:03:00',
            'DownloadUrl': 'https://secure.urkund.com/archive/download?c1=92305055&amp;c2=676372&amp;c3=525345',
            'OptOutInfo': {
                'Url': 'https://secure.urkund.com/account/document/exemptionstatus/92305055-676372-525345',
                'Message': 'As the author of the document you have submitted, it is within your right to hide '
                           'the text content from being viewed by other educational organisations. Note that by '
                           'hiding the text content, you will not delete the document. The document will remain '
                           'stored and checked against internal and external sources and forwarded to your tutor '
                           'along with a plagiarism report. The text content might also be visible within your '
                           'educational organisation, depending on their preferred settings. However, the text '
                           'content of the document will not be visible for any user outside your educational '
                           'organisation.\n\nBear in mind that by hiding your document, it will not be protected '
                           'against plagiarism. This means that an unauthorised person will be able to make use '
                           'of your work in the future. If you want to protect your copyright, you should leave '
                           'it unhidden.\n\nTo hide the text content of your document, click the below link:'}
        },
        'Report': {
            'Id': 88349077,
            'Significance': 5.86,
            'MatchCount': 833,
            'SourceCount': 75,
            'ReportUrl': 'https://secure.urkund.com/view/88349077-508223-368549',
            'Warnings': []
        },
        'Subject': '',
        'Message': '',
        'Anonymous': None,
        'AutoDeleteDocument': False,
        'MOCKED': True
    }]

    mocker.patch('urkund.urkund_lib.submissions.Submissions.result', return_value=mock_module)
