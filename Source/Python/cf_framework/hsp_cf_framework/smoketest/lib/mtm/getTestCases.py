# -*- coding: <encoding name> -*-
"""
####################################################################################
#Description : Methods generated for TFS & MTM API for Suites, test cases & reports
#Author      : Tejeswara Rao Kottapalli
#Modified by :
#Comments    :
###################################################################################
"""

import json
import logging
from configobj import ConfigObj
from utility import Utility
UtilityTest = Utility()

configFile = 'config.properties'
config = ConfigObj(configFile)


class GetTestCases:

    def __init__(self):
        """Class for using TFS/MTM Test Case Reporting
        """
        pass

    def get_all_steps_comments(self, test_script_log):
        test_steps = []
        for i in range(0, len(test_script_log)):
            step_status = test_script_log[i]['state']
            if step_status.lower() == 'passed':
                try:
                    if test_script_log[i].get('actualComment', '') != '':
                        actual_result = 'Verified Response is : ' + str(test_script_log[i]['actualComment'])
                    else:
                        actual_result = 'Verified Response Status Code. Status Code: ' + \
                                        str(test_script_log[i]['payload']['incomingRequest']['statusCode'])
                except:
                    actual_result = 'Verified functionality is working fine'
                step_status = 'Passed'
            else:
                if test_script_log[i].get('actualComment', '') != '':
                    actual_result = 'Functionality did not verify. Response is : ' + \
                                    str(test_script_log[i]['actualComment'])
                else:
                    actual_result = json.dumps(test_script_log[i]['err'])
                step_status = 'Failed'

            test_steps.append({
                "stepNumber": int(i + 1),
                "actualResponse": actual_result,
                "StepStatus": step_status
            })
        return test_steps

    def get_all_step_logs(self, test_script_log):
        step_report = []
        for i in range(0, len(test_script_log)):
            step_status = test_script_log[i]
            step_report.append(step_status)
        return step_report

    def get_test_case_field_values(self, test_case_id, client):
        tc_details = []
        tfs_tc_api = config.get('tfshostapi') + '/_apis/wit/workitems?ids=' + test_case_id + \
                     '&fields=System.id,Philips.UniqueID,System.Title,System.ChangedBy,' \
                     'Philips.Type,Microsoft.VSTS.TCM.AutomationStatus,Philips.' \
                     'SoapUIprojectfilePath,Microsoft.VSTS.TCM.Steps&api-version=1.0'

        get_tc_resp = UtilityTest.SendRequest('GET', tfs_tc_api, '', '', 'Y', '200', client)
        if str(get_tc_resp.status_code) == '200':
            tc_field_values = json.loads(get_tc_resp.text)
            tc_unique_id = str(tc_field_values['value'][0]['fields']['Philips.UniqueID'])
            tc_title = tc_field_values['value'][0]['fields']['System.Title'].encode('utf-8')
            tc_changedby = tc_field_values['value'][0]['fields']['System.ChangedBy'].encode('utf-8')
            tc_type = tc_field_values['value'][0]['fields']['Philips.Type'].encode('utf-8')
            tc_step_id = len(tc_field_values['value'][0]['fields']['Microsoft.VSTS.TCM.Steps'].encode(
                'utf-8').split('step id=')) - 1
            tc_step_type = len(tc_field_values['value'][0]['fields']['Microsoft.VSTS.TCM.Steps'].encode(
                'utf-8').split('step type=')) - 1
            tc_step_div_type = len(tc_field_values['value'][0]['fields']['Microsoft.VSTS.TCM.Steps'].encode(
                'utf-8').split('<DIV><P>')) - 1

            if int(tc_step_id) > 0:
                tc_step_count = int(tc_step_id)
            elif int(tc_step_type) > 0:
                tc_step_count = int(tc_step_type)
            elif int(tc_step_div_type) > 0:
                tc_step_count = int(tc_step_div_type)
            else:
                tc_step_count = 0
            tc_details.append(tc_unique_id)
            tc_details.append(tc_title)
            tc_details.append(tc_changedby)
            tc_details.append(tc_type)
            tc_details.append(tc_step_count)
            return tc_details

    def create_tc_report_json_for_mtm(self, tc_details, tc_id, tc_log, tc_point_id, tc_run_id, all_steps_results):
        tc_jsn_report = {}
        tc_jsn_report['uniqueId'] = tc_details[0]
        tc_jsn_report['testCaseId'] = tc_id
        tc_jsn_report['testPointId'] = tc_point_id
        tc_jsn_report['testRunId'] = tc_run_id
        #tc_jsn_report['testCaseStartTime'] = tc_log[0]['startTime']
        tc_jsn_report['testCaseDuration'] = ''
        tc_jsn_report['comments'] = 'Test is executed and Results are pushed to MTM'

        if int(tc_details[4]) == 1:
            tc_jsn_report['testSteps'] = all_steps_results
        else:
            tc_jsn_report['testSteps'] = all_steps_results

        test_case_status = 'Passed'
        if str(all_steps_results).find('Failed') is not -1:
            test_case_status = 'Failed'
        tc_jsn_report['testCaseStatus'] = test_case_status

        return json.dumps(tc_jsn_report), test_case_status

    def push_step_level_results_mtm(self, tc_json_report, client):
        customtfsapirsltupload = config.get('customtfshostapi') + '/UpdateTest/Json'
        logging.info(customtfsapirsltupload)
        logging.info(tc_json_report)
        resp = UtilityTest.SendRequest('POST', customtfsapirsltupload, tc_json_report, '', 'Y', '200', client)
        logging.info(resp.text)
        if str(resp.status_code) == '200':
            logging.info(
                'Test Case Step Level Report is uploaded to the test case in MTM')
        else:
            logging.error(
                'Test Case Step Level Report did not upload to the test case in MTM')

    def push_step_level_attachment_mtm(self, tc_log, tc_id, tc_point_id, tc_run_id, client):
        test_log = self.get_all_step_logs(tc_log)
        i = 1
        for step_log in test_log:
            customtfsapistepattachmentUpload = config.get(
                'customtfshostapi') + '/UploadTestStepAttachment/' + str(tc_run_id) + '/' + str(tc_id) + '/' + \
                                               str(tc_point_id) + '/' + str(i) + '?fileName=step_log.json'

            logging.info(customtfsapistepattachmentUpload)
            logging.info(json.dumps(step_log))
            steplvlAttach = UtilityTest.SendRequest(
                'POST', customtfsapistepattachmentUpload, json.dumps(step_log), '', 'Y', '200', client)
            i = i + 1

            logging.debug(steplvlAttach.text)
            logging.debug(steplvlAttach.status_code)
            if str(steplvlAttach.status_code) == '200':
                logging.info('Attached Test Case Step Level logs in MTM')
            else:
                logging.error(
                    'Did not Attach Test Case Step Level logs in MTM')

    def push_test_case_level_attachment_mtm (self, tc_log, tc_id, tc_point_id, tc_run_id, client, log_name):
        customtfsapiattachmentUpload = config.get('customtfshostapi') + '/UploadTestAttachment/' + str(
            tc_run_id) + '/' + str(tc_id) + '/' + str(tc_point_id) + '?fileName=' + log_name
        summaryLogresp = UtilityTest.SendRequest('POST', customtfsapiattachmentUpload, json.dumps(tc_log), '', 'Y',
                                                 '200',
                                                 client)
        if str(summaryLogresp.status_code) == '200':
            logging.info('Attached Summarry Log at Test Case Level in MTM')
        else:
            logging.error('Did not Summary Log at Test Case Level in MTM')


    # Get Test Case Test points
    def getTestCaseTestPoints(self, SuiteId, TcId, client, testplanid):
        logging.debug('Inside getTestCaseTestPoints')
        tp = ''
        tfsTCTPAPI = config.get('tfshostapi') + '/DHP/_apis/test/Plans/' + testplanid + \
            '/suites/' + SuiteId + '/points??testcaseid=' + TcId + '&includePointDetails=true'
        logging.debug(tfsTCTPAPI)
        getTCTPResp = UtilityTest.SendRequest('GET', tfsTCTPAPI, '', '', 'Y', '200', client)
        logging.debug(getTCTPResp.status_code)
        if str(getTCTPResp.status_code) == '200':
            jsnTPResp = json.loads(getTCTPResp.text)
            childTPLen = len(jsnTPResp['value'])
            if childTPLen <> 0:
                for n in range(0, childTPLen):
                    testcaseid = str(jsnTPResp['value'][n]['testCase']['id'].encode('utf-8'))
                    if str(testcaseid) == str(TcId):
                        tp = str(jsnTPResp['value'][n]['id'])
                        # logging.debug("Test Point is created. for test case id: %s and Test Point id: %s"%(str(TcId),str(tp))
                        logging.debug("Test Point is created. Test Point id: %s" % tp)
        else:
            logging.debug("Invalid Response. method_getAllSuiteIDs. Rest Request: %s" % tfsTCTPAPI)
        return tp

    # Get the test case testrunid based on test plan id and test case test point id
    def getTestRunID(self, testPlanId, testPointsId, client):
        logging.debug('Inside getTestRunID')
        reqURL = config.get('tfshostapi') + '/DHP/_apis/test/runs?api-version=1.0'
        payLoad = '{"name": "Create Test Run ID","comment":"Creation of Test Run ID for the test point id","plan": ' \
                  '{"id": ' + str(testPlanId) + '},"pointIds": [' + str(testPointsId) + ']}'
        header = {'Content-Type': 'application/json'}

        receivedResp = UtilityTest.SendRequest('POST', reqURL, payLoad, header, 'Y', '200', client)
        if receivedResp != 'REQUEST FAILED':
            respStatusCode = str(receivedResp.status_code)
            if str(respStatusCode) == '200':
                respText = receivedResp.text
                resp = json.loads(respText)
                # logging.debug('TestRunID is created. for test point id: %s and TestRunId: %s'%(testPointsId,resp.get('id'))
                logging.debug("TestRunID is created. TestRunId: %s" % resp.get('id'))
                return resp.get('id')
            else:
                logging.error("Rest Request is Failed. Request URL: %s" % reqURL)
        else:
            logging.error("Rest Request is Failed. Request URL: %s" % reqURL)


    # Get the list of test case ids exist in a suite
    def get_test_cases(self, SuiteId, client, testplanid):
        logging.debug('Inside getTestCases')
        test_case_ids = []

        tfsTCAPI = config.get('tfshostapi') + '/DHP/_apis/test/Plans/' + \
            testplanid + '/suites/' + SuiteId + '/testcases'
        logging.info(tfsTCAPI)

        getTCResp = UtilityTest.SendRequest('GET', tfsTCAPI, '', '', 'Y', '200', client)
        if str(getTCResp.status_code) == '200':
            jsnTCResp = json.loads(getTCResp.text)
            testcasesCount = jsnTCResp['count']
            if testcasesCount <> 0:
                for i in range(0, testcasesCount):
                    childSuite = str(jsnTCResp['value'][i]['testCase']['id'].encode('utf-8'))
                    test_case_ids.append(childSuite)
            else:
                logging.debug("No Test Cases are exist: test cases count: %s" %
                              (str(testcasesCount)))
        else:
            logging.debug("Invalid Response. method_getTestCases. Rest Requst: %s" % tfsTCAPI)
        logging.debug(test_case_ids)
        return test_case_ids

    def getAllSuiteIDs(self, SuiteId, client, testplanid):
        suites = []
        tfsSuiteAPI = config.get(
            'tfshostapi') + '/DHP/_apis/test/Plans/' + testplanid + '/suites/' + SuiteId + \
                      '?includeChildSuites=true&api-version=1.0'

        getSuiteResp = UtilityTest.SendRequest('GET', tfsSuiteAPI, '', '', 'Y', '200', client)
        if str(getSuiteResp.status_code) == '200':
            jsnResp = json.loads(getSuiteResp.text)

            testCaseCount = jsnResp['testCaseCount']
            if testCaseCount <> 0:
                suites.append(SuiteId)

            childSuiteLen = len(jsnResp['suites'])
            if childSuiteLen <> 0:
                for n in range(0, childSuiteLen):
                    childSuite = str(jsnResp['suites'][n]['id'].encode('utf-8'))
                    suites.extend(self.getAllSuiteIDs(str(childSuite), client, testplanid))
        else:
            logging.debug("Invalid Response. method_getAllSuiteIDs. Rest Requst: %s" % tfsSuiteAPI)

        logging.debug('Get All SuiteIDs')
        logging.debug(suites)
        return suites

    def get_test_result(self, json_obj, test_id):
        if isinstance(json_obj, dict):
            data_keys = json_obj.keys()
            for i in xrange(len(data_keys)):
                if data_keys[i] == 'title':
                    if test_id in json_obj[data_keys[i]] and test_id + '.' not in json_obj[data_keys[i]]:
                        return json_obj
                if data_keys[i] == 'TestUniqueID':
                    if test_id in json_obj[data_keys[i]]:
                        return json_obj
                else:
                    return_obj = self.get_test_result(json_obj[data_keys[i]], test_id)
                    if not (return_obj is None):
                        return return_obj

        elif isinstance(json_obj, list):
            for item in json_obj:
                return_obj = self.get_test_result(item, test_id)
                if not (return_obj is None):
                    return return_obj
