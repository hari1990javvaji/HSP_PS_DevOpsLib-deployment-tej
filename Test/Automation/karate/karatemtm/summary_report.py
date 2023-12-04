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
import logging
import time


class KPIQueries(object):

	def __init__(self):
		pass

	def create_request_session(self, user_name, password):
		session = requests.Session()
		session.auth = HttpNtlmAuth('code1\\'+user_name, password)
		return session

	def send_request(self, req_type, req_url, req_payload, req_headers, statusCode, client):
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

		os.environ['HTTP_PROXY'] = ''
		os.environ['HTTPS_PROXY'] = ''
		for x in range(0, 3):
			try:
				if req_type == "POST":
					logging.debug('Performing POST request for the request url: %s' % req_url)
					responseOutPut = client.post(req_url, data=dataVal, headers=req_headers)
				elif req_type == "GET":
					logging.debug('Performing GET request for the request url: %s' % req_url)
					responseOutPut = client.get(req_url)
					logging.info(req_url)
					logging.info(responseOutPut.text)

				if str(responseOutPut.status_code) == str(statusCode):
					break
				else:
					logging.debug('Wait for number of seconds and retry the request. Wait time: 10')
					time.sleep(5)

			except ConnectionError as e:
				responseOutPut = 'REQUEST FAILED'
				logging.debug(
					'Wait for number of seconds and retry the request. Wait time: 10')
				time.sleep(10)

		logging.debug("Rest Request Response: method_send_request. Request URL is: %s" % req_url)
		logging.debug(responseOutPut)

		return responseOutPut


	def get_tfs_custom_api_query_response(self,
										  method, req_url, req_body, req_header, status_code, resp_tag, client, retry):
		resp = self.send_request(method, req_url, req_body, req_header, status_code, client)
		if resp != '' and str(resp.status_code) == status_code:
			tree = ElementTree.fromstring(resp.text)
			for node in tree.iter():
				if resp_tag in node.tag:
					if node.text.isdigit() is True or node.text == 'OK':
						return node.text
					elif retry >= 1:
						logging.info('Retrying Custom REST Request Again')
						time.sleep(5)
						return self.get_tfs_custom_api_query_response(method,
																	  req_url,
																	  req_body,
																	  req_header,
																	  status_code, resp_tag, client, retry - 1)

	def getTFSRstForAllQueries(self,
							   user_name,
							   password, mtm_config_file, execution_result_file, execution_summary_file, log_level):

		test_summary = {}
		tfQueryRslt = {}
		mtm_config_file = open(mtm_config_file, 'r')
		mtm_config_obj = json.load(mtm_config_file)
		projectname = mtm_config_obj['projectname']
		projectrelease = mtm_config_obj['projectrelease']
		buildType = mtm_config_obj['buildType']
		customtfshostapi = mtm_config_obj['customtfshostapi']
		tfsquerypath = mtm_config_obj['tfsquerypath']
		total_tc = mtm_config_obj['total_tc']
		total_attc = mtm_config_obj['total_attc']
		total_reg_tc = mtm_config_obj['total_reg_tc']
		total_reg_attc = mtm_config_obj['total_reg_attc']
		total_non_reg_tc = mtm_config_obj['total_non_reg_tc']
		total_non_reg_attc = mtm_config_obj['total_non_reg_attc']
		total_reg_at_perf_tc = mtm_config_obj['total_reg_at_perf_tc']
		total_reg_at_sec_tc = mtm_config_obj['total_reg_at_sec_tc']
		apiretry = mtm_config_obj['apiretry']

		self.logging("", log_level)
		tfsQuery_total_tc = customtfshostapi + '/GetQueryCount?PsName=' + projectname + '&Release=' + \
							projectrelease + '&QueryPath=' + tfsquerypath + '/' + \
							str(buildType) + '/' + str(buildType) + '_' + total_tc
		tfsQuery_total_attc = customtfshostapi + '/GetQueryCount?PsName=' + projectname + '&Release=' + \
							  projectrelease + '&QueryPath=' + tfsquerypath + '/' + str(buildType) + '/' + \
							  str(buildType) + '_' + total_attc
		tfsQuery_total_reg_tc = customtfshostapi + '/GetQueryCount?PsName=' + projectname + '&Release=' + \
								projectrelease + '&QueryPath=' + tfsquerypath + '/' + str(buildType) + '/' + \
								str(buildType) + '_' + total_reg_tc
		tfsQuery_total_reg_attc = customtfshostapi + '/GetQueryCount?PsName=' + projectname + '&Release=' + \
								  projectrelease + '&QueryPath=' + tfsquerypath + '/' + str(buildType) + '/' + \
								  str(buildType) + '_' + total_reg_attc
		tfsQuery_total_non_reg_tc = customtfshostapi + '/GetQueryCount?PsName=' + projectname + '&Release=' + \
									projectrelease + '&QueryPath=' + tfsquerypath + '/' + str(buildType) + '/' + \
									str(buildType) + '_' + total_non_reg_tc
		tfsQuery_total_non_reg_attc = customtfshostapi + '/GetQueryCount?PsName=' + projectname + '&Release=' + \
									  projectrelease + '&QueryPath=' + tfsquerypath + '/' + str(buildType) + '/' + \
									  str(buildType) + '_' + total_non_reg_attc
		total_reg_at_perf_tc = customtfshostapi + '/GetQueryCount?PsName=' + projectname + '&Release=' + \
							   projectrelease + '&QueryPath=' + tfsquerypath + '/' + str(buildType) + '/' + \
							   str(buildType) + '_' + total_reg_at_perf_tc
		total_reg_at_sec_tc = customtfshostapi + '/GetQueryCount?PsName=' + projectname + '&Release=' + \
							  projectrelease + '&QueryPath=' + tfsquerypath + '/' + str(buildType) + '/' + \
							  str(buildType) + '_' + total_reg_at_sec_tc

		api_retry = int(apiretry)
		resp_tag = 'GetQueryCountfromStoredQueriesResult'
		client = self.create_request_session(user_name, password)
		tfQueryRslt['TotalTestCases'] = self.get_tfs_custom_api_query_response('GET', tfsQuery_total_tc, '', '',
																			   '200', resp_tag, client, api_retry)
		tfQueryRslt['AutomatedTestCases'] = self.get_tfs_custom_api_query_response('GET', tfsQuery_total_attc, '', '',
																				   '200', resp_tag, client, api_retry)
		tfQueryRslt['RegressionTestCases'] = self.get_tfs_custom_api_query_response('GET', tfsQuery_total_reg_tc,
																					'', '', '200', resp_tag, client,
																					api_retry)
		tfQueryRslt['RegressionAutomatedTestCases'] = self.get_tfs_custom_api_query_response('GET',
																							 tfsQuery_total_reg_attc,
																							 '', '', '200', resp_tag,
																							 client, api_retry)
		tfQueryRslt['NonRegressionTestCases'] = self.get_tfs_custom_api_query_response('GET',
																					   tfsQuery_total_non_reg_tc,
																					   '', '', '200', resp_tag,
																					   client, api_retry)
		tfQueryRslt['NonRegressionAutomatedTestCases'] = self.\
			get_tfs_custom_api_query_response('GET', tfsQuery_total_non_reg_attc, '', '', '200', resp_tag, client,
											  api_retry)
		tfQueryRslt['PerformanceAutomatedTestCases'] = self.\
			get_tfs_custom_api_query_response('GET', total_reg_at_perf_tc, '', '', '200', resp_tag, client, api_retry)
		tfQueryRslt['SecurityAutomatedTestCases'] = self.\
			get_tfs_custom_api_query_response('GET', total_reg_at_sec_tc, '', '', '200', resp_tag, client, api_retry)


		if os.path.exists(execution_result_file) is True:
			query_file = open(execution_result_file, 'r')
			query_obj = json.load(query_file)
			tfQueryRslt['TotalRegressionPassed'] = query_obj['TotalRegressionPassed']
			tfQueryRslt['TotalRegressionFailed'] = query_obj['TotalRegressionFailed']
			tfQueryRslt['TotalNonRegressionPassed'] = query_obj['TotalNonRegressionPassed']
			tfQueryRslt['TotalNonRegressionFailed'] = query_obj['TotalNonRegressionFailed']
		else:
			logging.error('ERROR: TFS Upload Execution Report did not generate')
			tfQueryRslt['TotalRegressionPassed'] = 0
			tfQueryRslt['TotalRegressionFailed'] = 0
			tfQueryRslt['TotalNonRegressionPassed'] = 0
			tfQueryRslt['TotalNonRegressionFailed'] = 0

		tfQueryRslt.update(test_summary)

		tfQueryJsn = json.dumps(tfQueryRslt)
		logging.info('Summary: %s' % tfQueryJsn)

		with open(execution_summary_file, 'w') as f:
			json.dump(tfQueryRslt, f, indent=2, ensure_ascii=False)


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


if __name__ == "__main__":
	KPIQueries_obj = KPIQueries()
	user_name = sys.argv[1]
	password = sys.argv[2]
	mtm_config_file = sys.argv[3]
	execution_result_file = sys.argv[4]
	execution_summary_file = sys.argv[5]
	log_level = sys.argv[6]
	KPIQueries_obj.getTFSRstForAllQueries(user_name,
										  password,
										  mtm_config_file,
										  execution_result_file,
										  execution_summary_file,
										  log_level)
