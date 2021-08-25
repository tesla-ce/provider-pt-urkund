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
""" TeSLA CE Urkund Plagiarism utility module """
import json
import os
import magic
import tempfile
import shutil
from tesla_ce_provider import message
import base64

FILENAME_CONTENT = 'content.txt'
TYPE_ASSIGN = 'assign'
TYPE_ASSIGN_ONLINE = 'assign_online'
TYPE_QUIZ_ATTEMPT = 'quiz_attempt'
TYPE_FORUM_POST = 'forum_post'


def get_decompress_files(sample_data, filename):
    # decompress files
    fp = tempfile.NamedTemporaryFile()
    fp.write(sample_data)
    fp.seek(0)

    tmp_filename = fp.name
    extract_directory = tempfile.TemporaryDirectory()
    # read data from file
    extension = filename.split('.')[-1]
    shutil.unpack_archive(tmp_filename, extract_directory.name, extension)

    return [os.listdir(extract_directory.name), extract_directory]


def get_sample_tree_files(sample_data, context, mimetype, filename, level, max_recursive_level, compressed_mimetypes,
                          accepted_mimetypes_provider, files_structure=None):
    """
        Get tree files from sample

        :param sample_data: Raw sample data
        :type sample_data: bytes
        :param context: Context of sample data
        :type context: dict
        :param mimetype: Mimetype of sample data
        :type mimetype: str
        :param filename: Filename of sample data
        :type filename: str
        :param level: Which level are actually analyzing inside file.
        :type level: int
        :param max_recursive_level: Max recursive level accepted
        :type max_recursive_level: int
        :param compressed_mimetypes: Accepted compressed mimetype values
        :type compressed_mimetypes: list
        :param accepted_mimetypes_provider: Accepted provider mimetypes
        :type accepted_mimetypes_provider: list
        :param files_structure: Files return structure
        :type files_structure: list
        :return: files_structure
        :rtype: list
    """
    if not files_structure:
        files_structure = []

    if level >= max_recursive_level:
        files_structure.append({
            "filename": filename,
            "mimetype": mimetype,
            "status": "REJECTED",
            "error": "MAX_RECURSIVE_LEVEL",
            "content": sample_data
        })
        return files_structure

    # check if context gets how to process this sample
    special_context_types = [TYPE_QUIZ_ATTEMPT, TYPE_FORUM_POST, TYPE_ASSIGN, TYPE_ASSIGN_ONLINE]
    if level == 0 and context.get('type') in special_context_types:
        [decompress_files, extract_directory] = get_decompress_files(sample_data, filename)

        # process as quiz_attempt, only process open_text responses
        content_raw_text = ''

        if os.path.isfile(extract_directory.name+os.path.sep+FILENAME_CONTENT):
            content = json.loads(extract_directory.name+os.path.sep+FILENAME_CONTENT)

            if context.get('type') == TYPE_ASSIGN_ONLINE or TYPE_ASSIGN:
                content_raw_text = content.get('online_text')
            elif content.get('type') == TYPE_FORUM_POST:
                content_raw_text = content.get('message')
            elif content.get('type') == TYPE_QUIZ_ATTEMPT:
                for attempt in content:
                    if attempt.get('open_text') is True:
                        content_raw_text += attempt.get('answer')+'\n\r'

            files_structure.append({
                "filename": context.get('type')+'.txt',
                "mimetype": 'text/plain',
                "status": "ACCEPTED",
                "content": content_raw_text
            })

        # check if sample has attachments
        for decompress_file in decompress_files:
            # skip content.txt file
            if decompress_file == FILENAME_CONTENT:
                continue

            new_filename = extract_directory.name+os.path.sep+decompress_file
            new_sample_data = None
            new_mimetype = 'directory'
            if os.path.isfile(new_filename):
                with open(new_filename, mode='rb') as file:
                    new_sample_data = base64.b64encode(file.read())

                new_mimetype = magic.from_file(new_filename, mime=True)

            files_structure = get_sample_tree_files(new_sample_data, context, new_mimetype, new_filename, level+1,
                                                    max_recursive_level, compressed_mimetypes,
                                                    accepted_mimetypes_provider, files_structure)
    elif mimetype == 'directory':
        for subitem in os.listdir(filename):
            new_filename = filename+os.path.sep+subitem
            new_sample_data = None
            new_mimetype = 'directory'
            if os.path.isfile(new_filename):
                with open(new_filename, mode='rb') as file:
                    new_sample_data = base64.b64encode(file.read())

                new_mimetype = magic.from_file(new_filename, mime=True)

            files_structure = get_sample_tree_files(new_sample_data, context, new_mimetype, new_filename, level+1,
                                                    max_recursive_level, compressed_mimetypes,
                                                    accepted_mimetypes_provider, files_structure)

    elif mimetype in compressed_mimetypes:
        # check if file is compress file
        [decompress_files, extract_directory] = get_decompress_files(sample_data, filename)

        for decompress_file in decompress_files:
            new_filename = extract_directory.name+os.path.sep+decompress_file
            new_sample_data = None
            new_mimetype = 'directory'
            if os.path.isfile(new_filename):
                with open(new_filename, mode='rb') as file:
                    new_sample_data = base64.b64encode(file.read())

                new_mimetype = magic.from_file(new_filename, mime=True)

            files_structure = get_sample_tree_files(new_sample_data, context, new_mimetype, new_filename, level+1,
                                                    max_recursive_level, compressed_mimetypes,
                                                    accepted_mimetypes_provider, files_structure)

    elif mimetype in accepted_mimetypes_provider:
        # append file directly
        files_structure.append({
            "filename": filename,
            "mimetype": mimetype,
            "status": "ACCEPTED",
            "content": sample_data
        })
    else:
        # todo: try extract text
        files_structure.append({
            "filename": filename,
            "mimetype": mimetype,
            "status": "REJECTED",
            "content": sample_data
        })

    return files_structure


def check_sample_file(sample, max_recursive_level, accepted_mimetypes=None, compressed_mimetypes=None,
                      accepted_mimetypes_provider=None):
    """
        Check sample information
        :param sample: Sample structure
        :type sample: Sample
        :param max_recursive_level: Maximum recursive level
        :type max_recursive_level: int
        :param accepted_mimetypes: Accepted mimetype values
        :type accepted_mimetypes: list
        :param compressed_mimetypes: Accepted compressed mimetype values
        :type compressed_mimetypes: list
        :param accepted_mimetypes_provider: Accepted provider mimetypes
        :type accepted_mimetypes_provider: list
        :return: An object with the image and mimetype or the found errors
        :rtype: dict
    """
    # Check mimetype
    mimetype = None
    sample_mimetype = None

    try:
        sample_mimetype = sample.data.split(',')[0].split(';')[0].split(':')[1]
    except Exception:
        return {
            'valid': False,
            'msg': "Mimetype is not in sample base64 data",
            'code': message.Provider.PROVIDER_INVALID_MIMETYPE.value,
            'file': None
        }

    mimetype = sample.metadata['mimetype']

    if sample_mimetype != mimetype:
        return {
            'valid': False,
            'msg': "Mimetype in sample data differs from sample mimetype",
            'code': message.Provider.PROVIDER_INVALID_MIMETYPE.value,
            'file': None
        }

    if mimetype not in accepted_mimetypes + accepted_mimetypes_provider + compressed_mimetypes:
        return {
            'valid': False,
            'msg': "Invalid mimetype. Accepted types are: [{}]".format(', '.join(accepted_mimetypes)),
            'code': message.Provider.PROVIDER_INVALID_MIMETYPE.value,
            'file': None
        }

    # Open file
    try:
        data = sample.data.split(',')[1]
    except (AttributeError, IndexError):
        return {
            'valid': False,
            'msg': "Invalid format sample data.",
            'code': message.Provider.PROVIDER_INVALID_SAMPLE_DATA.value,
            'file': None
        }

    tree_files = None
    try:
        sample_data = base64.b64decode(data)
        filename = sample.metadata['filename']
        tree_files = get_sample_tree_files(sample_data, sample.context, mimetype, filename, 0, max_recursive_level,
                                           compressed_mimetypes, accepted_mimetypes_provider)

    except base64.binascii.Error:
        return {
            'valid': False,
            'msg': "Invalid format sample data. Invalid base 64 format.",
            'code': message.Provider.PROVIDER_INVALID_SAMPLE_DATA.value,
            'file': None
        }

    if tree_files is None:
        return {
            'valid': False,
            'msg': "Invalid format sample data. Error build file tree.",
            'code': message.Provider.PROVIDER_INVALID_SAMPLE_DATA.value,
            'file': None
        }

    return {
        'valid': True,
        'mimetype': mimetype,
        'tree_file': tree_files
    }
