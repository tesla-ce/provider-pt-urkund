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
""" TeSLA CE Urkund Plagiarism module """
import os
import uuid

from tesla_ce_provider import BaseProvider, result, message
from tesla_ce_provider.provider.audit.tp import PlagiarismAudit
from . import utils
from ..urkund_lib import UrkundLib
from ..urkund_lib.exceptions import BaseUrkundLibException, MediaTypeNotSupported, RequestTooLarge, BadRequest, Timeout


class UrkundProvider(BaseProvider):
    """
        TeSLA Face Recognition implementation
    """
    accepted_mimetypes_urkund = [
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.sun.xml.writer',
        'application/vnd.ms-powerpoint',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'application/pdf',
        'text/plain',
        'application/rtf',
        'text/html',
        'text/html',
        'application/vnd.ms-works',
        'application/vnd.oasis.opendocument.text'
    ]

    compressed_mimetypes = [
        'application/zip',
        'application/gzip',
        'application/x-tar',
        'application/x-bzip2',
        'application/x-7z-compressed',
        'application/x-rar-compressed',
        'application/x-lzma'
    ]

    accepted_mimetypes = accepted_mimetypes_urkund + compressed_mimetypes

    config = {
        'user': os.getenv('URKUND_USER', None),
        'password': os.getenv('URKUND_PASSWORD', None),
        'unit': os.getenv('URKUND_UNIT', None),
        'organization': os.getenv('URKUND_ORGANIZATION', None),
        'sub_organization': os.getenv('URKUND_SUBORGANIZATION', None),
        'default_email_receiver': os.getenv('URKUND_DEFAULT_EMAIL_RECEIVER', None),
        'compression_recursive_extract_level': 3,
        'timeout_retries': 0,
        'max_timeout_retries': 3,
        'timeout_between_retries': 60,
        'countdown_multiplier': 2,
        'countdown_initial': 5
    }
    _urkund_lib = None

    def _get_urkund_lib(self):
        """
        Return UrkundLib instance
        :return:
        """
        if self._urkund_lib is None:
            self._urkund_lib = UrkundLib(user=self.config['user'], password=self.config['password'],
                                         unit=self.config['unit'], organization=self.config['organization'],
                                         sub_organization=self.config['sub_organization'])

        return self._urkund_lib

    def set_options(self, options):
        """
            Set options for the provider
            :param options: Provider options following provider options_scheme definition
            :type options: dict
        """
        if options is not None:
            permitted_options = self.config.keys()

            for permitted_option in permitted_options:
                if permitted_option in options:
                    self.config[permitted_option] = options[permitted_option]

    def verify(self, request, model):
        """
            Verify a learner request
            :param request: Verification request
            :type request: Request
            :param model: Provider model
            :type model: dict
            :return: Verification result
            :rtype: tesla_provider.VerificationResult
        """

        # Check provided input
        sample_check = utils.check_sample_file(request, self.config['compression_recursive_extract_level'],
                                               self.accepted_mimetypes, self.compressed_mimetypes,
                                               self.accepted_mimetypes_urkund)

        if not sample_check['valid']:
            return result.VerificationResult(False, error_message=sample_check['msg'],
                                             message_code=sample_check['code'])

        # sample is valid proceed to sent to urkund
        receiver = self._get_urkund_lib().receivers.get_by_email(self.config['default_email_receiver'])

        idx = 0
        info = {
            "learner_id": request.learner_id,
            "request_id": request.request_id,
            "external_ids": [],
            "processed_external_ids": {
                "errors": [],
                "corrects": []
            },
            "errors": [],
            "countdown": self.config['countdown_initial'],
            "total_files": len(sample_check['tree_file'])
        }

        for f in sample_check['tree_file']:
            if f['status'] == 'ACCEPTED':
                file = {
                    "filename": f['filename'],
                    "mimetype": f['mimetype'],
                    "content": f['content']
                }
                external_id = "{}_{}".format(request.request_id, idx)

                email = "{}{}".format(request.learner_id, self._get_urkund_lib().receivers.get_suffix())
                try:
                    response = self._get_urkund_lib().submissions.send(external_id=external_id, file=file,
                                                                       analysis_email=receiver['AnalysisAddress'],
                                                                       email=email)

                    if response['Status']['State'] in ('Submitted', 'Accepted', 'Analyzed'):
                        aux = {
                            "external_id": external_id,
                            "analysis_email": receiver['AnalysisAddress'],
                            "filename": f['filename']
                        }
                        info['external_ids'].append(aux)

                    elif response['Status']['State'] == 'Error':
                        urkund_code = self._get_urkund_lib().submissions.\
                            get_message_from_submission_error(response['Status']['ErrorCode'])

                        aux = {
                            "code": message.provider.Provider.PROVIDER_INVALID_SAMPLE_DATA,
                            "filename": f['filename'],
                            "urkund_code": urkund_code,
                            "urkund_message": response['Status']['Message']
                        }
                        info['processed_external_ids']['errors'].append(aux)

                    else:
                        aux = {
                            "code": message.provider.Provider.PROVIDER_INVALID_SAMPLE_DATA,
                            "filename": f['filename'],
                            "urkund_code": None,
                            "urkund_message": response['Status']['Message']
                        }
                        info['processed_external_ids']['errors'].append(aux)

                    idx += 1
                except Timeout:
                    self.config['timeout_retries'] += 1
                    if self.config['timeout_retries'] >= self.config['max_timeout_retries']:
                        aux = {
                            "code": message.provider.Provider.PROVIDER_EXTERNAL_SERVICE_TIMEOUT,
                            "filename": f['filename'],
                            "urkund_code": None,
                            "urkund_message": None
                        }
                        info['processed_external_ids']['errors'].append(aux)
                    else:
                        return self.verify(request, model)

                except MediaTypeNotSupported:
                    aux = {
                        "code": message.provider.Provider.PROVIDER_INVALID_MIMETYPE,
                        "filename": f['filename'],
                        "urkund_code": None,
                        "urkund_message": None
                    }
                    info['processed_external_ids']['errors'].append(aux)
                except (BadRequest, RequestTooLarge, BaseUrkundLibException):
                    aux = {
                        "code": message.provider.Provider.PROVIDER_INVALID_SAMPLE_DATA,
                        "filename": f['filename'],
                        "urkund_code": None,
                        "urkund_message": None
                    }
                    info['processed_external_ids']['errors'].append(aux)

        # check if there is any sent document valid to check in the future
        if len(info['external_ids']) == 0:
            return result.VerificationResult(False, message_code=message.provider.Provider.PROVIDER_INVALID_SAMPLE_DATA)

        key = "tukrund_check_data_{}".format(uuid.uuid4())
        notification = result.NotificationTask(key, countdown=info['countdown']*60, info=info)
        self.update_or_create_notification(notification)

        return result.VerificationDelayedResult(learner_id=request.learner_id, request_id=request.request_id,
                                                result=result.VerificationResult(True))

    def on_notification(self, key, info):
        """
            Respond to a notification task
            :param key: The notification task unique key
            :type key: str
            :param info: Information stored in the notification
            :type info: dict

            self.update_or_create_notification(result.NotificationTask('key', countdown=30, info={'my_field': 3}))
        """

        if key.startswith('tukrund_check_data'):
            new_info = {
                "learner_id": info['learner_id'],
                "request_id": info['request_id'],
                "external_ids": [],
                "processed_external_ids": {
                    "errors": [],
                    "corrects": []
                },
                "errors": [],
                "countdown": self.config['countdown_initial'] * self.config['countdown_multiplier']
            }

            # check for every external_id if Urkund has result
            for r in info['external_ids']:
                responses = self._get_urkund_lib().submissions.result(external_id=r['external_id'],
                                                                      analysis_email=r['analysis_email'])

                for response in responses:
                    if response['Status']['State'] == 'Analyzed':
                        # return response OK
                        aux = {
                            "external_id": r['external_id'],
                            "analysis_email": r['analysis_email'],
                            "filename": r['filename'],
                            "report_url": response['Report']['ReportUrl'],
                            "significance": response['Report']['Significance'],
                            "match_count": response['Report']['MatchCount'],
                            "source_count": response['Report']['SourceCount'],
                            "warnings": response['Report']['Warnings']
                        }
                        new_info['processed_external_ids']['corrects'].append(aux)

                    elif response['Status']['State'] == 'Error':
                        # return response KO
                        urkund_code = self._get_urkund_lib().submissions. \
                            get_message_from_submission_error(response['Status']['ErrorCode'])

                        aux = {
                            "code": message.provider.Provider.PROVIDER_INVALID_SAMPLE_DATA,
                            "filename": r['filename'],
                            "urkund_code": urkund_code,
                            "urkund_message": response['Status']['Message']
                        }

                        new_info['processed_external_ids']['errors'].append(aux)
                    else:
                        # put in next check
                        new_info['external_ids'].append(r)

            # decide if all requests are processed
            num_errors = len(new_info['processed_external_ids']['errors'])
            num_corrects = len(new_info['processed_external_ids']['corrects'])
            total_processed = num_errors + num_corrects

            if info['total_files'] == total_processed:
                # we can return result from this request
                if num_errors < num_corrects:
                    code_alert = result.VerificationResult.AlertCode.OK
                else:
                    code_alert = result.VerificationResult.AlertCode.WARNING

                audit = PlagiarismAudit(documents=new_info['processed_external_ids'],
                                        total_documents=num_errors+num_corrects,
                                        total_documents_accepted=num_corrects,
                                        total_documents_rejected=num_errors)
                max_significance = 0

                for correct in new_info['processed_external_ids']['corrects']:
                    if correct["significance"] > max_significance:
                        max_significance = correct["significance"]

                    audit.add_comparison(comparison_id=correct['external_id'], result=correct['significance'],
                                         extra_info=correct)

                result_obj = result.VerificationResult(True, code=code_alert, audit=audit, result=max_significance)
                verif_delayed_result = result.VerificationDelayedResult(learner_id=info['learner_id'],
                                                                        request_id=info['request_id'],
                                                                        result=result_obj, info=None)
                self.update_delayed_result(verif_delayed_result)
            else:
                # create new notification
                key = "tukrund_check_data_{}".format(uuid.uuid4())
                notification = result.NotificationTask(key, countdown=info['countdown']*60, info=info)
                self.update_or_create_notification(notification)

