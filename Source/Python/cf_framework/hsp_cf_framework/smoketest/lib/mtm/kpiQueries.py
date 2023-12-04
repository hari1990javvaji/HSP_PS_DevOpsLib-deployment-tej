'''
###########################################################################
#Description : Methods generated for reporting the results to MTM
#Author      : Tejeswara Rao Kottapalli
#Modified by :
#Comments    :
###########################################################################
'''
from xml.etree import ElementTree
import json
import logging
from configobj import ConfigObj
from utility import Utility
UtilityTestTCRT = Utility()

configFile = 'config.properties'
config = ConfigObj(configFile)

class KPIQueries(object):

	def getTFSQueryResult(self, tfsquery, client):
		resp = UtilityTestTCRT.SendRequest('GET', tfsquery, '', '', 'Y', '200', client)
		tree = ElementTree.fromstring(resp.text)
		for node in tree.iter():
			node.tag
			if 'GetQueryCountfromStoredQueriesResult' in node.tag:
				return node.text

	def getTFSRstForAllQueries(self, buildType, tarLocation, client, projectname, projectrelease):
		tfQueryRslt = {}
		tfsQuery_total_tc = config.get('customtfshostapi') + '/GetQueryCount?PsName=' + projectname + '&Release=' + projectrelease + '&QueryPath=' + config.get('tfsquerypath') + '/' + str(buildType) + '/' + str(buildType) + '_' + config.get('total_tc')
		tfsQuery_total_attc = config.get('customtfshostapi') + '/GetQueryCount?PsName=' + projectname + '&Release=' + projectrelease + '&QueryPath=' + config.get('tfsquerypath') + '/' + str(buildType) + '/' + str(buildType) + '_' + config.get('total_attc')
		tfsQuery_total_reg_tc = config.get('customtfshostapi') + '/GetQueryCount?PsName=' + projectname + '&Release=' + projectrelease + '&QueryPath=' + config.get('tfsquerypath') + '/' + str(buildType) + '/' + str(buildType) + '_' + config.get('total_reg_tc')
		tfsQuery_total_reg_attc = config.get('customtfshostapi') + '/GetQueryCount?PsName=' + projectname + '&Release=' + projectrelease + '&QueryPath=' + config.get('tfsquerypath') + '/' + str(buildType) + '/' + str(buildType) + '_' + config.get('total_reg_attc')
		tfsQuery_total_non_reg_tc = config.get('customtfshostapi') + '/GetQueryCount?PsName=' + projectname + '&Release=' + projectrelease + '&QueryPath=' + config.get('tfsquerypath') + '/' + str(buildType) + '/' + str(buildType) + '_' + config.get('total_non_reg_tc')
		tfsQuery_total_non_reg_attc = config.get('customtfshostapi') + '/GetQueryCount?PsName=' + projectname + '&Release=' + projectrelease + '&QueryPath=' + config.get('tfsquerypath') + '/' + str(buildType) + '/' + str(buildType) + '_' + config.get('total_non_reg_attc')
		logging.info (tfsQuery_total_tc)

		tfQueryRslt['TotalTestCases'] = self.getTFSQueryResult(tfsQuery_total_tc, client)
		tfQueryRslt['AutomatedTestCases'] = self.getTFSQueryResult(tfsQuery_total_attc, client)
		tfQueryRslt['RegressionTestCases'] = self.getTFSQueryResult(tfsQuery_total_reg_tc, client)
		tfQueryRslt['RegressionAutomatedTestCases'] = self.getTFSQueryResult(
			tfsQuery_total_reg_attc, client)
		tfQueryRslt['NonRegressionTestCases'] = self.getTFSQueryResult(tfsQuery_total_non_reg_tc, client)
		tfQueryRslt['NonRegressionAutomatedTestCases'] = self.getTFSQueryResult(
			tfsQuery_total_non_reg_attc, client)
		tfQueryJsn = json.dumps(tfQueryRslt)
		logging.info('TFS Query Json: %s' % tfQueryJsn)

		jsnFilePath = tarLocation + '/tfs_query_result.json'

		with open(jsnFilePath, 'w') as f:
			json.dump(tfQueryRslt, f, ensure_ascii=False)