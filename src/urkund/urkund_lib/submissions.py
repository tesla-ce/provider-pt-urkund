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
import base64
import urllib


class Submissions:
    """
    Submissions class
    """
    organization = None
    request = None

    def __init__(self, organization, request):
        self.organization = organization
        self.request = request

    def send(self, external_id, file, analysis_email, email):
        """
        Send submission
        :param external_id:
        :param file:
        :param analysis_email:
        :param email:
        :return:
        """
        receiver_url_encoded = urllib.parse.quote(analysis_email)

        filename_only = base64.b64encode(file['filename'].split('/')[-1].encode('utf-8')).decode('utf-8', 'ignore')
        file['content'] = base64.b64decode(file['content'].decode('utf-8', 'ignore'))

        headers = {'Content-Type': file['mimetype'], 'x-urkund-anonymous': '0', 'x-urkund-message': '',
                   'x-urkund-subject': '', 'x-urkund-submitter': email, 'x-urkund-filename': str(filename_only),
                   'Content-Length': str(len(file['content']))}

        return self.request.make(verb='POST', url='submissions/'+str(receiver_url_encoded)+"/"+str(external_id),
                                 headers=headers, data=file['content'])

    def result(self, external_id, analysis_email):
        """
        Get result of submission
        :param external_id:
        :param analysis_email:
        :return:
        """
        receiver_url_encoded = urllib.parse.quote(analysis_email)
        return self.request.make(verb='GET', url='submissions/'+str(receiver_url_encoded)+"/"+str(external_id))

    @staticmethod
    def get_message_from_submission_error(error):
        explication_errors = {
            3: "The submitted document does not contain enough text to be analysed",
            4: "Document submitted after deadline",
            5000: "General error during analysis process",
            5001: "Failed to generate report",
            7001: "Indexinf failed"
        }

        if int(error) in explication_errors.keys():
            return explication_errors[int(error)]

        return "Error not explained"

