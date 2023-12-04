"""
# File Name:    Utility.py
# Description:  File contains list of methods to generated to verify REST API testing using Python.r
"""


import requests
import json
import configparser
import sys
import os
from requests.exceptions import ConnectionError
import jmespath
from time import time
import time
import shutil
from random import SystemRandom
import random
import string
from random import randint
import re
import logging
import subprocess
from pathlib import Path
import datetime
from datetime import timedelta
from builtins import range
cryptogen = SystemRandom()


class Utility(object):

    def load_prop_file(self, file_path, sep='=', comment_char='#'):
        """
        Read the file passed as parameter as a properties file.
        """
        props = {}
        try:
            with open(file_path, "rt") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith(comment_char):
                        key_value = line.split(sep)
                        key = key_value[0].strip()
                        value = sep.join(key_value[1:]).strip().strip('"')
                        props[key] = value
        except:
            logging.error("Error: ", sys.exc_info()[1])
        return props

    def get_prop_value(self, file_path, prop_name):
        prp_dict = self.load_prop_file(file_path, sep='=', comment_char='#')
        try:
            return prp_dict[prop_name]
        except KeyError:
            logging.error("Error: ", sys.exc_info()[1])
            return 'Error'

    def get_prop_val_by_section(self, file_path, section, prop_name):
        config = configparser.SafeConfigParser()
        config.read(file_path)
        try:
            return config.get(section, prop_name)
        except:
            #logging.error("Error: ", sys.exc_info()[1])
            return 'ERROR'

    def add_update_val_in_prop_file_by_section(self, file_path, section, prop_name, prop_val):
        config = configparser.SafeConfigParser()
        config.read(file_path)
        config.set(section, prop_name, prop_val)
        with open(file_path, 'w') as configfile:
            config.write(configfile)

    def delete_file(self, file_path):
        flag = 'False'
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.debug("File is deleted. File Name: " + file_path)
            flag = 'True'
        return flag

    def write_to_file(self, file_path, content):
        flag = 'False'
        with open(file_path, 'w') as outfile:
            outfile.write(content)
            flag = 'True'
        return flag

    def read_file(self, file_path):
        file_path = file_path.replace('\\', '/')
        return open(file_path, 'r').read()

    def random_string(self, length):
        letters = string.ascii_lowercase
        return ''.join(cryptogen.choice(letters) for i in range(length))

    def random_integer(self, length):
        range_start = 10 ** (length - 1)
        range_end = (10 ** length) - 1
        return cryptogen.randrange(range_start, range_end)

    def random_string_integer(self, length):
        return str(self.random_string(length)) + str(self.random_integer(length))

    # @staticmethod
    def find_parameters_list(self, file_object):
        replaced = re.findall(r'(?<=\{).+?(?=\})', file_object)
        return len(replaced), replaced

    # @staticmethod
    def update_parameter_values(self, file_object):
        rtn = self.find_parameters_list(file_object)
        in_param_length = rtn[0]
        in_param_list = rtn[1]

        for i in range(in_param_length):
            in_param_split = in_param_list[i].split('|')

            if len(in_param_split) == 1:
                prop_val = self.get_prop_value('config.properties', in_param_split[0])
                file_object = self.find_replace_text(file_object, '{' + in_param_split[0] + '}', prop_val)

            elif len(in_param_split) == 2:
                if in_param_split[1] == 'APP' or in_param_split[1] == 'STATIC' or in_param_split[1] == 'RUNTIME':
                    prop_val = self.get_prop_val_by_section('config.properties', in_param_split[1],
                                                                   in_param_split[0])
                    file_object = self.find_replace_text(file_object, '{' + in_param_list[i] + '}', prop_val)
                elif in_param_split[0] == 'RNDSTR':
                    random_string = self.random_string(int(in_param_split[1]))
                    file_object = self.find_replace_text(file_object, '{' + in_param_list[i] + '}',
                                                                random_string)
                elif in_param_split[0] == 'RNDINT':
                    random_int = self.random_integer(int(in_param_split[1]))
                    file_object = self.find_replace_text(file_object, '{' + in_param_list[i] + '}',
                                                                random_int)
                elif in_param_split[0] == 'RND':
                    random_str_int = self.random_string_integer(int(in_param_split[1]))
                    file_object = self.find_replace_text(file_object, '{' + in_param_list[i] + '}',
                                                                random_str_int)
                else:
                    file_object = self.find_replace_text(file_object, '{' + in_param_list[i] + '}',
                                                                in_param_split[1])

            elif len(in_param_split) == 3:
                if in_param_split[1] == 'RNDSTR':
                    random_string = self.random_string(int(in_param_split[2]))
                    file_object = self.find_replace_text(file_object, '{' + in_param_list[i] + '}',
                                                                random_string)
                    self.add_update_val_in_prop_file_by_section('config.properties', 'RUNTIME',
                                                                       in_param_split[0], random_string)
                elif in_param_split[1] == 'RNDINT':
                    random_int = self.random_integer(int(in_param_split[2]))
                    file_object = self.find_replace_text(file_object, '{' + in_param_list[i] + '}',
                                                                str(random_int))
                    self.add_update_val_in_prop_file_by_section('config.properties', 'RUNTIME',
                                                                       in_param_split[0], random_int)
                elif in_param_split[1] == 'RND':
                    random_str_int = self.random_string_integer(int(in_param_split[2]))
                    file_object = self.find_replace_text(file_object, '{' + in_param_list[i] + '}',
                                                                random_str_int)
                    self.add_update_val_in_prop_file_by_section('config.properties', 'RUNTIME',
                                                                       in_param_split[0], random_str_int)
        return file_object

    def delete_first_last_chars_file_obj(self, file_name):
        try:
            with open(file_name, 'rb+') as f:
                f.seek(0, 2)
                size = f.tell()
                f.truncate(size - 1)
            f.close()

            f = open(file_name)
            lines = f.readlines()
            f.close()

            f = open(file_name, 'w')
            for line in lines:
                f.write(line[1:])
            f.close()

            return 'UPDATED'
        except:
            return 'ERROR'

    def find_string_in_file_obj(self, file_path, find_string):
        verify_status = []
        data = open(file_path).read()
        position = data.find(find_string)
        if position != -1:
            status = "Pass"
            logging.info("Found at position", position)
            result = "Response is verified. Verified Text is: " + find_string
        else:
            status = 'Fail'
            result = "Did not verify the response. Text is not verified: " + find_string

        verify_status.append(status)
        verify_status.append(result)
        return verify_status

    def find_string_from_obj(self, output_obj, find_string):
        verify_status = []
        if find_string in output_obj:
            status = 'Pass'
            result = "Response is verified. Verified Text is: " + find_string
        else:
            status = 'Fail'
            result = "Did not verify the response. Text is not verified: " + find_string

        verify_status.append(status)
        verify_status.append(result)
        return verify_status

    def find_replace_text(self, obj, find_string, replace_string):
        return obj.replace(find_string, replace_string)

    def replace_string_in_file(self, file_path, find_string, replace_string):
        try:
            fs = open(file_path, 'r')
            file_obj = fs.read()
            fs.close()

            updated_obj = file_obj.replace(find_string, replace_string)
            fs = open(file_path, 'w')
            fs.write(updated_obj)
            fs.close()
        except:
            logging.error("Error: ", sys.exc_info()[1])
            return 'ERROR'

    def copy_file(self, source_dir, source_file, destination_dir, destination_file):
        source_full_path = source_dir + '/' + source_file
        destination_full_path = destination_dir + '/' + destination_file

        self.delete_file(destination_full_path)
        try:
            shutil.copyfile(source_full_path, destination_full_path)
            return destination_full_path
        except:
            logging.error("Error: ", sys.exc_info()[1])
            return 'ERROR'

    def copy_file_with_same_extension (self, source_dir, source_file):
        file_name, file_ext = os.path.splitext(source_file)
        copyFile = file_name + "_Copy" + file_ext
        copy_file_full_path = source_dir + copyFile
        self.delete_file(copy_file_full_path)
        shutil.copyfile(source_dir + source_file, copy_file_full_path)
        return copy_file_full_path

    def get_file_name_extension(self, src_file):
        file_name, file_ext = os.path.splitext(src_file)
        return file_name, file_ext

    def send_api_request (self, req_type, url, payload, headers, cert, status_code):
        response = ''
        actual_status_code = ''
        response_time = 0.0
        if (self.get_prop_val_by_section('config.properties', 'STATIC', 'proxy')).lower() == 'y':
            os.environ['HTTP_PROXY'] = self.get_prop_val_by_section('config.properties', 'STATIC', 'http_proxy')
            os.environ['HTTPS_PROXY'] = self.get_prop_val_by_section('config.properties', 'STATIC', 'https_proxy')
        else:
            os.environ['HTTP_PROXY'] = ''
            os.environ['HTTPS_PROXY'] = ''

        req_retry = self.get_prop_val_by_section('config.properties', 'STATIC', 'request_retry')
        for x in range(0, int(req_retry)):
            try:
                start_time = time.time()
                if req_type == "POST":
                    response = requests.post(url, data=payload, headers=headers, cert=cert, verify=True)

                elif req_type == "GET":
                    response = requests.get(url, headers=headers, cert=cert, verify=True)

                elif req_type == "PUT":
                    response = requests.put(url, data=payload, headers=headers, cert=cert, verify=True)

                elif req_type == "DELETE":
                    response = requests.delete(url, data=payload, headers=headers, cert=cert, verify=True)

                elif req_type == "OPTIONS":
                    response = requests.options(url)
                end_time = time.time()
                response_time = round((end_time - start_time), 5)

                if str(response.status_code) == str(status_code):
                    actual_status_code = response.status_code
                    break
                else:
                    actual_status_code = response.status_code
                    time.sleep(int(self.get_prop_val_by_section('config.properties',
                                                                'STATIC',
                                                                'request_retry_wait_seconds')))

            except ConnectionError as e:
                response = 'REQUEST FAILED'
                actual_status_code = 0
                time.sleep(int(self.get_prop_val_by_section('config.properties',
                                                            'STATIC',
                                                            'request_retry_wait_seconds')))
        return response, actual_status_code, response_time

    def get_param_val_from_file (self, response_obj, param_name):
        string_exist = "False"
        param_val = ''

        data = response_obj.replace('\\', '').replace(',n', ',').replace('{n ', '{').replace('"n}', '"}')
        split_file_content = data.split(",")
        for x in range(0, len(split_file_content)):
            if '"' + param_name + '"' in split_file_content[x]:

                tag_split = split_file_content[x].split(':')
                for y in range(0, len(tag_split)):
                    if '"' + param_name + '"' in tag_split[y]:
                        tag_split_val = tag_split[y + 1]

                        if (tag_split_val == '"http') or (tag_split_val == '"https'):
                            tag_split_val = tag_split[y + 1] + ":" + tag_split[y + 2]
                        tag_split_val_len = tag_split_val.split('":"')
                        if tag_split[y] == '{"lastUpdated"':
                            tag_split_val = tag_split[2] + ":" + tag_split[3] + ":" + tag_split[4].replace('}', '')

                        if len(tag_split_val_len) > 1:
                            tag_split_val = tag_split_val_len[0]
                            if (tag_split_val == '"http') or (tag_split_val == '"https'):
                                tag_split_val = tag_split_val_len[0] + ":" + tag_split_val_len[0]
                        param_val = tag_split_val.replace('"', '').replace('}', '').replace('{', '').\
                            replace(']', '').replace('[', '')
                        string_exist = "True"
                        break
                break
        if string_exist == "True":
            return param_val.strip()
        else:
            return string_exist

    def update_prop_from_response(self, config_prop_file, response_obj, prop_name):
        split_prop_name = prop_name.split('#')
        for x in range(0, len(split_prop_name)):
            splitPropName = split_prop_name[x].split('|')
            if len(splitPropName) == 2:
                pram_val = self.get_param_val_from_file(response_obj, splitPropName[1])
                pram_val = pram_val.replace("\\", "")
                self.add_update_val_in_prop_file_by_section(config_prop_file,
                                                            'RUNTIME',
                                                            splitPropName[0] + splitPropName[1],
                                                            pram_val)
            else:
                pram_val = self.get_param_val_from_file(response_obj, split_prop_name[x])
                pram_val = pram_val.replace("\\", "")
                self.add_update_val_in_prop_file_by_section(config_prop_file, 'RUNTIME', split_prop_name[x], pram_val)
            logging.debug(split_prop_name[x] + ' : ' + pram_val)

    def update_prop_from_response_jsonpath(self, config_prop_file, response_obj, prop_name):
        split_prop_name = prop_name.split('#')
        for x in range(0, len(split_prop_name)):
            split_prop_name = split_prop_name[x].split('|')
            # pramValue = self.JsonFileReader(responseJson, splitPropName[1])
            pram_val = jmespath.search(split_prop_name[1], response_obj)
            self.add_update_val_in_prop_file_by_section(config_prop_file,
                                                        'RUNTIME',
                                                        split_prop_name[0] + split_prop_name[2],
                                                        pram_val)
            if pram_val is None:
                pram_val = 'False'
            logging.debug(split_prop_name[0] + split_prop_name[2] + ' : ' + pram_val)

    def json_file_reader(self, file_name, attribute_xpath):
        with open(file_name) as f:
            jsonblob = json.load(f)
            return jmespath.search(attribute_xpath, jsonblob)

    def update_prop_from_response_header(self, config_prop_file, response_obj, prop_name):
        split_prop_name = prop_name.split('#')
        for x in range(0, len(split_prop_name)):
            splitPropName = split_prop_name[x].split('|')
            if len(splitPropName) == 2:
                resp_header = response_obj[splitPropName[1]]
                self.add_update_val_in_prop_file_by_section(config_prop_file, 'RUNTIME',
                                                            splitPropName[0] + splitPropName[2], resp_header)
            else:
                resp_header = response_obj[split_prop_name[x]]
                self.add_update_val_in_prop_file_by_section(config_prop_file, 'RUNTIME', split_prop_name[x],
                                                            resp_header)

            logging.debug(split_prop_name[x] + ' : ' + resp_header)

    def VerifyResponse (self, receivedResponse, expectedValue):
        FailFlags = ''
        AppendResult = ''
        verStatus = 'False'
        expectedRslLst = expectedValue.split('#')
        for y in range(0, len(expectedRslLst)):
            expVal = expectedRslLst[y]
            expValSplit = expVal.split('|')
            if len(expValSplit) == 2:
                if ':' in expValSplit[0]:
                    splitexpVal = expValSplit[0].split(":")
                    getFirstString = (splitexpVal[1])[:1]
                    spaceExist = ''
                    if getFirstString == ' ':
                        spaceExist = 'True'
                        trimParam = splitexpVal[1].strip()
                    else:
                        trimParam = splitexpVal[1]

                    if expValSplit[1] == 'RUNTIME':
                        expSubVal = self.get_prop_val_by_section('config.properties', 'RUNTIME', trimParam)
                    elif  expValSplit[1] == 'STATIC':
                        expSubVal = self.get_prop_val_by_section('config.properties', 'STATIC', trimParam)

                    if spaceExist == 'True':
                        expVal = splitexpVal[0] + ': ' + expSubVal
                    else:
                        expVal = splitexpVal[0] + ':' + expSubVal

                elif '=' in expValSplit[0]:
                    splitexpVal = expValSplit[0].split("=")
                    getFirstString = (splitexpVal[1])[:1]
                    spaceExist = ''
                    if getFirstString == ' ':
                        spaceExist = 'True'
                        trimParam = splitexpVal[1].strip()
                    else:
                        trimParam = splitexpVal[1]

                    if expValSplit[1] == 'RUNTIME':
                        expSubVal = self.get_prop_val_by_section('config.properties', 'RUNTIME', trimParam)
                    elif  expValSplit[1] == 'STATIC':
                        expSubVal = self.get_prop_val_by_section('config.properties', 'STATIC', trimParam)

                    if spaceExist == 'True':
                        expVal = splitexpVal[0] + '= ' + expSubVal
                    else:
                        expVal = splitexpVal[0] + '=' + expSubVal
                else:
                    if expValSplit[1] == 'RUNTIME':
                        expVal = self.get_prop_val_by_section('config.properties', 'RUNTIME', expValSplit[0])
                    elif  expValSplit[1] == 'STATIC':
                        expVal = self.get_prop_val_by_section('config.properties', 'STATIC', expValSplit[0])

            logging.info( "Expected Value to be verified in the response= " + expVal)
            responseMessage = receivedResponse.replace('"', '').replace('"', '')
            testResult = self.find_string_from_obj(responseMessage.lower(), expVal.lower())
            logging.info(testResult)

            if testResult[0] == 'Fail':
                FailFlags = FailFlags + expVal + ' '
            else:
                AppendResult = AppendResult + expVal + ' '

        if FailFlags == '':
            verStatus = 'True'
        return verStatus, AppendResult, FailFlags

    def log1(self, config_file, log_location, log_file_no_ext):
        log_level = self.get_prop_val_by_section(config_file, 'STATIC', 'log_level')

        """ Setting log levels """
        if log_location != '':
            log_location = log_location + '/'

        if log_file_no_ext != '':
            log_file_no_ext = log_file_no_ext + '_'

        if log_level == 'info':
            logging.basicConfig(filename=log_location + "info.log",
                                level=logging.INFO,
                                format="%(asctime)s:%(levelname)s:%(message)s")
        elif log_level == 'debug':
            logging.basicConfig(filename=log_location + (log_file_no_ext + "debug.log").strip(),
                                level=logging.DEBUG,
                                format="%(asctime)s:%(levelname)s:%(message)s")
        elif log_level == 'error':
            logging.basicConfig(filename=log_location + (log_file_no_ext + "error.log").strip(),
                                level=logging.ERROR,
                                format="%(asctime)s:%(levelname)s:%(message)s")

    def logging1(self, log_location):
        config_file = os.getcwd().replace('\\', '/') + '/config.properties'
        log_level = self.get_prop_val_by_section(config_file, 'STATIC', 'log_level')

        """ Setting log levels """
        if log_location != '':
            log_location = log_location + '/'

        if log_level == 'info':
            logging.basicConfig(filename=log_location + "info.log", level=logging.INFO,
                                format="%(asctime)s:%(levelname)s:%(message)s")
        elif log_level == 'debug':
            logging.basicConfig(filename=log_location + "debug.log", level=logging.DEBUG,
                                format="%(asctime)s:%(levelname)s:%(message)s")
        elif log_level == 'error':
            logging.basicConfig(filename=log_location + "error.log", level=logging.ERROR,
                                format="%(asctime)s:%(levelname)s:%(message)s")

    def setup_logger1(self, logger_name, log_file):
        l = logging.getLogger(logger_name)
        formatter = logging.Formatter('"%(asctime)s:%(levelname)s:%(message)s"')
        fileHandler = logging.FileHandler(log_file, mode='a')
        fileHandler.setFormatter(formatter)
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)

        l.setLevel(logging.INFO)
        l.addHandler(fileHandler)
        l.addHandler(streamHandler)
        return l

    def setup_logger(self, logger_name, log_file, log_level):
        logger = logging.getLogger(logger_name)
        logger.propagate = False
        if log_level.lower() == 'debug':
            logger.setLevel(logging.DEBUG)
        elif log_level.lower() == 'error':
            logger.setLevel(logging.ERROR)
        else:
            logger.setLevel(logging.INFO)
        logger.handlers = []
        formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
        handler = logging.FileHandler(log_file, mode='w')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def createDirPath_LongFileDeleteIfExist(self, path):
        pathCreate = os.path.dirname(path + '/')
        if os.path.exists(pathCreate) is False:
            os.makedirs(path)
        else:
            try:
                shutil.rmtree(pathCreate)
                if os.path.exists(pathCreate) is False:
                    os.makedirs(pathCreate)
                logging.debug('Created Directory. Path : %s' % pathCreate)
            except:
                pathEmpty = str(Path(pathCreate).parents[0]).replace('\\', '/')
                folderPath = pathEmpty + '/empty'
                if os.path.exists(folderPath) is False:
                    os.makedirs(folderPath)
                delFiles = ['robocopy', '/MIR', folderPath, pathCreate]
                try:
                    subprocess.Popen(delFiles, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    logging.info('Deleted long file names using robocopy. Directory Path : %s' % pathCreate)
                except:
                    pass
                if os.path.exists(pathCreate) is False:
                    os.makedirs(pathCreate)
                pass

    def moveDirectoryLevelUp(self, dirPath, level):
        return str(Path(dirPath).parents[int(level)]).replace('\\', '/')

    def add_suite_ids(self, json_file, *argv):
        suite_id = {}
        suite_ids = []
        jsn_file = open(json_file, 'r')
        json_obj = json.load(jsn_file)

        for arg in argv:
            suite_ids.append(arg)
        suite_id['suiteIDs'] = suite_ids
        json_obj['stats'] = suite_id

        with open(json_file, 'w') as file_object:
            json.dump(json_obj, file_object, indent=4)

        return json_obj

    def find_file(self, root_dir, file_name):
        """ with name of root dir and file name
         It will traverse and get the full file path.
         No file defined, then returns all csv full file paths """

        file_path = []
        for root, dir, file in os.walk(root_dir):
            for name in file:
                if file_name != '':
                    for split_file in file_name.split(','):
                        if name.lower() == split_file.lower():
                            file_path.append(os.path.join(root, name).replace('\\', '/'))
                elif name.endswith(".csv"):
                    file_path.append(os.path.join(root, name).replace('\\', '/'))
        return file_path


    def logging(self, log_location, log_level):
        """ Setting log levels """
        if log_location != '':
            log_location = log_location + '/'

        if log_level.lower() == 'info':
            logging.basicConfig(filename=log_location + "console_info.log", level=logging.INFO,
                                format="%(asctime)s:%(levelname)s:%(message)s")
            logging.getLogger().addHandler(logging.StreamHandler())
        elif log_level.lower() == 'debug':
            logging.basicConfig(filename=log_location + "console_debug.log", level=logging.DEBUG,
                                format="%(asctime)s:%(levelname)s:%(message)s")
            logging.getLogger().addHandler(logging.StreamHandler())

        elif log_level.lower() == 'error':
            logging.basicConfig(filename=log_location + "console_error.log", level=logging.ERROR,
                                format="%(asctime)s:%(levelname)s:%(message)s")
            logging.getLogger().addHandler(logging.StreamHandler())

