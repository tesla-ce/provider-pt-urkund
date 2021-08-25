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
import uuid
from datetime import datetime
import os
import base64


def get_request(filename, mimetype, learner_id = None):
    from tesla_ce_provider.models.base import Request

    if learner_id is None:
        learner_id = str(uuid.uuid4())

    filename = os.path.dirname(os.path.realpath(__file__)) + '/data/' + filename

    with open(filename, mode='rb') as file:
        filename_content64 = base64.b64encode(file.read())

    now = datetime.now()
    request_id = datetime.timestamp(now)

    realfilename = filename.split('/')[-1]

    sample_data = {
        "learner_id": learner_id,
        "data": "data:{};base64,{}".format(mimetype, filename_content64.decode('utf-8')),
        "instruments": [6],
        "metadata": {
            "context": {},
            "mimetype": mimetype,
            "filename": realfilename
        }
    }
    return Request({
        'id': request_id,
        'learner_id': learner_id,
        'data': sample_data,
        'validations': []
    })
