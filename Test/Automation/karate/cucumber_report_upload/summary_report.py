"""
###########################################################################
#Description : Methods generated for reporting the results to MTM
#Author      : Tejeswara Rao Kottapalli
#Modified by :
#Comments    :
###########################################################################
"""

import os
import sys
import requests
from requests.exceptions import ConnectionError
from requests_ntlm import HttpNtlmAuth
from xml.etree import ElementTree
import json
import time
import ConfigParser
from generate_html_reports import html_report


def create_request_session(user_name, password):

    session = requests.Session()
    session.auth = HttpNtlmAuth('code1\\'+user_name, password)
    return session


def send_request(req_type, req_url, req_payload, req_headers, status_code, client):
    response = ''
    payload_obj = ''
    if req_payload != '':
        file_name, file_ext = os.path.splitext(req_payload)
        if file_ext == '.txt':
            payload_obj = open(req_payload).read()
        elif file_ext == '.json':
            payload = json.load(open(req_payload))
            payload_obj = json.dumps(payload)
        else:
            payload_obj = req_payload

    os.environ['HTTP_PROXY'] = ''
    os.environ['HTTPS_PROXY'] = ''
    for x in range(0, 3):
        try:
            if req_type == "POST":
                print('Performing POST request for the request url: %s' % req_url)
                response = client.post(req_url, data=payload_obj, headers=req_headers)
            elif req_type == "GET":
                print('Performing GET request for the request url: %s' % req_url)
                response = client.get(req_url)
                print(req_url)
                print(response.text)

            if str(response.status_code) == str(status_code):
                break
            else:
                print('Wait for number of seconds and retry the request. Wait time: 10')
                time.sleep(5)

        except ConnectionError as e:
            print (e)
            response = 'REQUEST FAILED'
            print(
                'Wait for number of seconds and retry the request. Wait time: 10')
            time.sleep(10)

    print("Rest Request Response: method_send_request. Request URL is: %s" % req_url)
    print(response)

    return response


def get_prop_val_by_section(file_path, section, prop_name):
    config = ConfigParser.RawConfigParser()
    config.read(file_path)
    try:
        return config.get(section, prop_name)
    except:
        return 'ERROR'


def get_tfs_custom_api_query_response(method, req_url, req_body, req_header, status_code, resp_tag, client, retry):
    resp = send_request(method, req_url, req_body, req_header, status_code, client)
    if resp != '' and str(resp.status_code) == status_code:
        tree = ElementTree.fromstring(resp.text)
        for node in tree.iter():
            if resp_tag in node.tag:
                if node.text.isdigit() is True or node.text == 'OK':
                    return node.text
                elif retry >= 1:
                    print('Retrying Custom REST Request Again')
                    time.sleep(5)
                    return get_tfs_custom_api_query_response(method,
                                                                  req_url,
                                                                  req_body,
                                                                  req_header,
                                                                  status_code, resp_tag, client, retry - 1)


def get_service_execution_report(user_name,
                                 password,
                                 project_prop_file,
                                 execution_result_file,
                                 reg_json_file_path,
                                 non_reg_json_file_path,
                                 report_location):

    test_summary = {}
    tfs_query_list = {}

    project_name = get_prop_val_by_section(project_prop_file, 'GLOBAL', 'project_name')
    project_release = get_prop_val_by_section(project_prop_file, 'GLOBAL', 'project_release')
    custom_tfs_api_host = get_prop_val_by_section(project_prop_file, 'GLOBAL', 'customtfshostapi')

    build_type = 'TEST'
    tfs_query_path = 'Shared Queries/Team Testing/CICD_Queries_GIT'
    total_tc = 'Total_TestCases'
    total_auto_tc = 'Automated_TestCases'
    total_reg_tc = 'Regression_TestCases'
    total_reg_attc = 'Regression_Automated_TestCases'
    total_non_reg_tc = 'Non_Regression_TestCases'
    total_non_reg_auto_tc = 'Non_Regression_Automated_TestCases'
    total_reg_at_perf_tc = 'Regression_Automated_Performance_TestCases'
    total_reg_at_sec_tc = 'Regression_Automated_Security_TestCases'
    api_retry = '3'

    tfsQuery_total_tc = custom_tfs_api_host + '/GetQueryCount?PsName=' + project_name + \
                        '&Release=' + project_release + '&QueryPath=' + tfs_query_path + '/' + \
                        str(build_type) + '/' + str(build_type) + '_' + total_tc
    tfsQuery_total_attc = custom_tfs_api_host + '/GetQueryCount?PsName=' + project_name + '&Release=' + \
                          project_release + '&QueryPath=' + tfs_query_path + '/' + str(build_type) + '/' + \
                          str(build_type) + '_' + total_auto_tc
    tfsQuery_total_reg_tc = custom_tfs_api_host + '/GetQueryCount?PsName=' + project_name + '&Release=' + \
                            project_release + '&QueryPath=' + tfs_query_path + '/' + str(build_type) + '/' + \
                            str(build_type) + '_' + total_reg_tc
    tfsQuery_total_reg_attc = custom_tfs_api_host + '/GetQueryCount?PsName=' + project_name + '&Release=' + \
                              project_release + '&QueryPath=' + tfs_query_path + '/' + str(build_type) + '/' + \
                              str(build_type) + '_' + total_reg_attc
    tfsQuery_total_non_reg_tc = custom_tfs_api_host + '/GetQueryCount?PsName=' + project_name + '&Release=' + \
                                project_release + '&QueryPath=' + tfs_query_path + '/' + str(build_type) + '/' + \
                                str(build_type) + '_' + total_non_reg_tc
    tfsQuery_total_non_reg_attc = custom_tfs_api_host + '/GetQueryCount?PsName=' + project_name + '&Release=' + \
                                  project_release + '&QueryPath=' + tfs_query_path + '/' + str(build_type) + '/' + \
                                  str(build_type) + '_' + total_non_reg_auto_tc
    total_reg_at_perf_tc = custom_tfs_api_host + '/GetQueryCount?PsName=' + project_name + '&Release=' + \
                           project_release + '&QueryPath=' + tfs_query_path + '/' + str(build_type) + '/' + \
                           str(build_type) + '_' + total_reg_at_perf_tc
    total_reg_at_sec_tc = custom_tfs_api_host + '/GetQueryCount?PsName=' + project_name + '&Release=' + \
                          project_release + '&QueryPath=' + tfs_query_path + '/' + str(build_type) + '/' + \
                          str(build_type) + '_' + total_reg_at_sec_tc

    api_retry = int(api_retry)
    resp_tag = 'GetQueryCountfromStoredQueriesResult'
    client = create_request_session(user_name, password)

    tfs_query_list['TotalTestCases'] = get_tfs_custom_api_query_response('GET', tfsQuery_total_tc, '', '', '200',
                                                                         resp_tag, client, api_retry)
    tfs_query_list['AutomatedTestCases'] = get_tfs_custom_api_query_response('GET', tfsQuery_total_attc, '', '',
                                                                               '200', resp_tag, client, api_retry)
    tfs_query_list['RegressionTestCases'] = get_tfs_custom_api_query_response('GET', tfsQuery_total_reg_tc,
                                                                                '', '', '200', resp_tag, client,
                                                                                api_retry)
    tfs_query_list['RegressionAutomatedTestCases'] = get_tfs_custom_api_query_response('GET',
                                                                                         tfsQuery_total_reg_attc,
                                                                                         '', '', '200', resp_tag,
                                                                                         client, api_retry)
    tfs_query_list['NonRegressionTestCases'] = get_tfs_custom_api_query_response('GET',
                                                                                   tfsQuery_total_non_reg_tc,
                                                                                   '', '', '200', resp_tag,
                                                                                   client, api_retry)
    tfs_query_list['NonRegressionAutomatedTestCases'] = \
        get_tfs_custom_api_query_response('GET', tfsQuery_total_non_reg_attc, '', '', '200', resp_tag, client,
                                          api_retry)
    tfs_query_list['PerformanceAutomatedTestCases'] = \
        get_tfs_custom_api_query_response('GET', total_reg_at_perf_tc, '', '', '200', resp_tag, client, api_retry)
    tfs_query_list['SecurityAutomatedTestCases'] = \
        get_tfs_custom_api_query_response('GET', total_reg_at_sec_tc, '', '', '200', resp_tag, client, api_retry)

    if os.path.exists(execution_result_file) is True:
        query_file = open(execution_result_file, 'r')
        query_obj = json.load(query_file)
        tfs_query_list['TotalRegressionPassed'] = query_obj['TotalRegressionPassed']
        tfs_query_list['TotalRegressionFailed'] = query_obj['TotalRegressionFailed']
        tfs_query_list['TotalNonRegressionPassed'] = query_obj['TotalNonRegressionPassed']
        tfs_query_list['TotalNonRegressionFailed'] = query_obj['TotalNonRegressionFailed']
    else:
        print('ERROR: TFS Upload Execution Report did not generate')
        tfs_query_list['TotalRegressionPassed'] = 0
        tfs_query_list['TotalRegressionFailed'] = 0
        tfs_query_list['TotalNonRegressionPassed'] = 0
        tfs_query_list['TotalNonRegressionFailed'] = 0

    tfs_query_list.update(test_summary)
	
    print('')
    tfs_query_jsn_obj = json.dumps(tfs_query_list)
    print('Summary: %s' % tfs_query_jsn_obj)

    test_summary = report_location + '/Test_Summary.json'
    with open(report_location + '/Test_Summary.json', 'w') as f:
        json.dump(tfs_query_list, f, ensure_ascii=False, indent=2)
	
    print('')
    'Generate HTML Reports'
    html_report(reg_json_file_path, non_reg_json_file_path, test_summary, report_location)


if __name__ == "__main__":
    user_name = sys.argv[1]
    password = sys.argv[2]
    project_prop_file = sys.argv[3]
    execution_result_file = sys.argv[4]
    reg_json_file_path = sys.argv[5]
    non_reg_json_file_path = sys.argv[6]
    report_location = sys.argv[7]

    get_service_execution_report (user_name,
                                  password,
                                  project_prop_file,
                                  execution_result_file,
                                  reg_json_file_path,
                                  non_reg_json_file_path,
                                  report_location)
