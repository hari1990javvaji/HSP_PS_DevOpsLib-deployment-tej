# -*- coding: <encoding name> -*-
"""
#############################################################################################################
#Description : Driver script to read nodejs report and upload the report in MTM and also generate HTML report
#Author      : Tejeswara Rao Kottapalli
#Modified by :
#Comments    :
#############################################################################################################
"""

import os
import sys
import json
from configobj import ConfigObj
from utility import Utility
from getTestCases import GetTestCases
from jsonHTML import htmlConvertion
from kpiQueries import KPIQueries

html_convert = htmlConvertion()
KPIQueriesTest = KPIQueries()

UtilityTest = Utility()
GetTestCasesTest = GetTestCases()
configFile = 'config.properties'
config = ConfigObj(configFile)

'''
user_name = sys.argv[1]
password = sys.argv[2]
project_name = sys.argv[3]
project_release = sys.argv[4]
test_plan = sys.argv[5]
automation_log = sys.argv[6]
log_location = sys.argv[7]
buildType = sys.argv[8]
'''

UtilityTest.logging(log_location)
client = UtilityTest.create_request_session(user_name, password)


'''Check log location where current framework logs will be stored. If not it will store in default location'''
if log_location != '':
    log_location = log_location.replace('\\','/') + '/'

'''Get TFS Test Case Query details for KPI Dashboard'''
print ''
print('Get TFS Test Case Query details for KPI Dashboard')
KPIQueriesTest.getTFSRstForAllQueries(buildType, log_location, client, project_name, project_release)
print('TFS Test Case Query details file is generated for KPI Dashboard file')


'''Read NODE JS Test Execution Report and Update the results in MTM'''
print ''
print('Read NODE JS Test Execution Report and Update the results in MTM')
read_auto_log = json.load(open(automation_log, 'r'))
for nodejs_suite_id in read_auto_log['stats']['suiteIDs']:
    suite_id_list = GetTestCasesTest.getAllSuiteIDs(str(nodejs_suite_id), client, test_plan)
    tescaselst = {}
    tescaselst['Suites'] = []
    suiteidlist = []
    print suite_id_list

    for suite_id in suite_id_list:
        tc_id_list = GetTestCasesTest.get_test_cases(suite_id, client, test_plan)
        if len(tc_id_list) != 0:
            testcaselst = []
            for tc_id in tc_id_list:
                tc_details = GetTestCasesTest.get_test_case_field_values(tc_id, client)
                test_object = GetTestCasesTest.get_test_result(read_auto_log, tc_details[0])
                if not (test_object is None):
                    print 'Pushing Results for The Test Case Unique ID: '+tc_details[0]
                    '''
                    tc_steps_log = test_object['tests']
                    '''
                    print test_object
                    if test_object.get('tests') is not None:
                        tc_steps_log = test_object['tests']
                    elif test_object.get('Steps') is not None:
                        tc_steps_log = test_object['Steps']
                    else:
                        tc_steps_log = []

                    stepResult = []
                    testStep = {}
                    all_steps_results = GetTestCasesTest.get_all_steps_comments(tc_steps_log)

                    ''' Generate Test Point ID for a test case'''
                    tc_point_id = GetTestCasesTest.getTestCaseTestPoints(suite_id, tc_id, client,
                                                                         test_plan)

                    ''' Generate Test Run ID for Test Case Instance'''
                    tc_run_id = GetTestCasesTest.getTestRunID(test_plan, tc_point_id, client)

                    ''' Generate Test Case Report json object for pushing the step level result '''
                    tc_json_report = GetTestCasesTest.create_tc_report_json_for_mtm(tc_details, tc_id, tc_steps_log,
                                                                                    tc_point_id, tc_run_id,
                                                                                    all_steps_results)

                    ''' Push Results to MTM Test Case - Steps, Pass/Fail, Overall test case pass/fail '''
                    GetTestCasesTest.push_step_level_results_mtm(tc_json_report[0], client)


                    ''' Attach Result at Test Case Step Level '''
                    if config.get('attachsteplogs') == 'true':
                        GetTestCasesTest.push_step_level_attachment_mtm(tc_steps_log, tc_id, tc_point_id, tc_run_id,
                                                                        client)

                    ''' Attach Result at Test Case Level '''
                    if config.get('attachsummarylog') == 'true':

                        if test_object.get('LogLocation') is not None:
                            log_file = test_object['LogLocation'] + '/' + tc_details[0] + '.log'
                            print log_file
                            if os.path.exists(log_file):
                                test_object = open(log_file, 'r').read()
                                print test_object
                                GetTestCasesTest.push_test_case_level_attachment_mtm(test_object, tc_id, tc_point_id,
                                                                                     tc_run_id,
                                                                                     client, 'test_summary.log')

                        GetTestCasesTest.push_test_case_level_attachment_mtm(test_object, tc_id, tc_point_id,
                                                                             tc_run_id,
                                                                             client, 'test_summary_log.json')

                    print 'Results are uploaded in MTM for The Test Case Unique ID: ' + tc_details[0]
                    print ''

                    '''Get list of test cases which are executed along with test case details'''
                    testcaselst.append({
                        'tcId': tc_id,
                        'uniqueId': tc_details[0],
                        'title': tc_details[1],
                        'changedby': tc_details[2],
                        'tcType': tc_details[3],
                        'tcResultLog': config.get('tfshostapi') + '/DHP/_TestManagement/runs?runId=' + str(
                            tc_run_id) + '&resultId=100000&_a=resultSummary',
                        'testRunStatus': tc_json_report[1]
                    })

            suiteidlist.append({
                "SuiteID": suite_id,
            'testcases': testcaselst
            })
        tescaselst['Suites'] = suiteidlist

    ''' Generate testcases json file for all executed test cases '''
    with open(log_location + 'testcases.json', 'w') as f:
        json.dump(tescaselst, f, ensure_ascii=False)

    print 'ALL VALID TEST CASE RESULTS ARE UPLOADED in MTM'



''' Generate HTML report for all test cases '''
print ''
print 'Generate HTML File'
html_convert.htmlFileConvertion(log_location + 'testcases.json',
                                log_location + 'tfs_query_result.json',
                                os.getcwd().replace('\\','/') + '/html_structure.html',
                                log_location + 'TEST_SUITE_REPORT.html')
print 'HTML File is generated. Location: '+ log_location + 'TEST_SUITE_REPORT.html'
