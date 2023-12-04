# -*- coding: <encoding name> -*-
'''
###########################################################################
#Description : Methods generated for TFS & MTM API for Suites and testcases
#Author      : Tejeswara Rao Kottapalli
#Modified by :
#Comments    :
###########################################################################
'''
import requests
import os
from requests.exceptions import ConnectionError
from requests_ntlm import HttpNtlmAuth
import json
from configobj import ConfigObj
import shutil
import logging
import time
from pathlib import Path
import subprocess

configFile = 'config.properties'
config = ConfigObj(configFile)


class Utility():

    def create_request_session(self, user_name, password):
        session = requests.Session()
        session.auth = HttpNtlmAuth('code1\\'+user_name, password)
        return session

    def SendRequest(self, req_type, req_url, req_payload, req_headers, setProxy, statusCode, client):
        responseOutPut = ''
        dataVal = ''
        if req_payload <> '':

            fileNa, fileExt = os.path.splitext(req_payload)
            if (fileExt == '.txt'):
                dataVal = open(req_payload).read()
            elif (fileExt == '.json'):
                payload = json.load(open(req_payload))
                dataVal = json.dumps(payload)
            else:
                dataVal = req_payload

        if setProxy == 'Y' or setProxy == 'y':
            os.environ['HTTP_PROXY'] = config.get('Http_proxy')
            os.environ['HTTPS_PROXY'] = config.get('Https_proxy')
        else:
            os.environ['HTTP_PROXY'] = ''
            os.environ['HTTPS_PROXY'] = ''

        # cred = (config.get('domain')+'\\'+ config.get('username'),config.get('password'))
        for x in range(0, int(config.get('apiretry'))):
            try:
                if req_type == "POST":
                    logging.debug('Performing POST request for the request url: %s' % req_url)
                    responseOutPut = client.post(req_url, data=dataVal, headers=req_headers)
                elif req_type == "GET":
                    logging.debug('Performing GET request for the request url: %s' % req_url)
                    responseOutPut = client.get(req_url)

                if str(responseOutPut.status_code) == str(statusCode):
                    break
                else:
                    logging.debug('Wait for number of seconds and retry the request. Wait time: %s' % config.get(
                        'apiretrywaittime'))
                    time.sleep(int(config.get('apiretrywaittime')))

            except ConnectionError as e:
                responseOutPut = 'REQUEST FAILED'
                logging.debug(
                    'Wait for number of seconds and retry the request. Wait time: %s' % config.get('apiretrywaittime'))
                time.sleep(int(config.get('apiretrywaittime')))

        logging.debug("Rest Request Response: method_SendRequest. Request URL is: %s" % req_url)
        logging.debug(responseOutPut)

        return responseOutPut

    def createDirPath(self, path):
        pathCreate = os.path.dirname(path + '/')
        if os.path.exists(pathCreate):
            try:
                shutil.rmtree(pathCreate)
                logging.debug('Remove Directory. Path : %s' % pathCreate)
            except OSError, e:
                logging.error("Error: %s - %s." % (e.filename, e.strerror))
        os.makedirs(pathCreate)

    def get_subdirs(self, dir):
        "Get a list of immediate subdirectories"
        return next(os.walk(dir))[1]

    def deleteImmidateChildDirs(self, dirPath):
        subdirlist = self.get_subdirs(dirPath)
        if len(subdirlist) > 0:
            for i in range(0, len(subdirlist)):
                shutil.rmtree(dirPath + '/' + subdirlist[i])

    def verifyFileExist(self, fileName):
        flag = 'false'
        if os.path.exists(fileName):
            flag = 'true'
            logging.debug('Verify File Exist. File : %s' % fileName)
        return flag

    def getFileSize(self, fileName):
        fileSize = 0
        fileExist = self.verifyFileExist(fileName)
        if fileExist == 'true':
            fileSize = os.path.getsize(fileName)
            logging.debug('Get File Size. File : %s and Size: %s' % (fileName, fileSize))
        return fileExist, fileSize

    def readJsonFile(self, fileName):
        fileObject = open(fileName, 'r')
        return json.load(fileObject)

    def moveDirectoryLevelUp(self, dirPath, level):
        return str(Path(dirPath).parents[int(level)]).replace('\\', '/')

    def convertMillsecondsToHourMinSec(self, millisec):
        millis = int(millisec)
        hours = (millis / (1000 * 60 * 60)) % 24
        if int(hours) < 10:
            hours = '0' + str(hours)
        minutes = (millis / (1000 * 60)) % 60
        if int(minutes) < 10:
            minutes = '0' + str(minutes)
        seconds = (millis / 1000) % 60
        if int(seconds) < 10:
            seconds = '0' + str(seconds)

        return str(hours) + ":" + str(minutes) + ":" + str(seconds)

    def createDirPath_LongFileDeleteIfExist(self, path):
        pathCreate = os.path.dirname(path + '/')
        if os.path.exists(pathCreate) == False:
            os.makedirs(path)
        else:
            try:
                shutil.rmtree(pathCreate)
                if os.path.exists(pathCreate) == False:
                    os.makedirs(pathCreate)
                logging.debug('Created Directory. Path : %s' % pathCreate)
            except:
                # logging.error("Error: %s - %s." % (e.filename, e.strerror))
                pathEmpty = str(Path(pathCreate).parents[0]).replace('\\', '/')
                folderPath = pathEmpty + '/empty'
                if os.path.exists(folderPath) == False:
                    os.makedirs(folderPath)
                delFiles = ['robocopy', '/MIR', folderPath, pathCreate]
                try:
                    proc = subprocess.Popen(delFiles, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    logging.info('Deleted long file names using robocopy. Directory Path : %s' % pathCreate)
                except:
                    pass
                if os.path.exists(pathCreate) == False:
                    os.makedirs(pathCreate)
                pass

    def logging(self, log_location):
        """ Setting log levels """
        if log_location != '':
            log_location = log_location + '/'

        if config.get('loglevel') == 'info':
            logging.basicConfig(filename=log_location + "info.log", level=logging.INFO,
                                format="%(asctime)s:%(levelname)s:%(message)s")
        elif config.get('loglevel') == 'debug':
            logging.basicConfig(filename=log_location + "debug.log", level=logging.DEBUG,
                                format="%(asctime)s:%(levelname)s:%(message)s")
        elif config.get('loglevel') == 'error':
            logging.basicConfig(filename=log_location + "error.log", level=logging.ERROR,
                                format="%(asctime)s:%(levelname)s:%(message)s")