# -*- coding: <encoding name> -*-
"""
############################################################################
#Description : Convert Json files to a single HTML file
#Author      : Sirisha
#Modified by : Tejeswara Rao Kottapalli
#Comments    :
############################################################################
"""

import jinja2
import json
import os
import traceback


class htmlConvertion():


    def read_json_file(self, fileName):
        try:
            fileObject = open(fileName, 'r')
            return json.load(fileObject)
        except:
            traceback.print_exc()
            return None

    def runStatus(self, json_file):
        count_pass = 0
        count_fail = 0
        for i in json_file['Suites']:
            m_dict =i
            for j in m_dict['testcases']:
                if j['testRunStatus']=='Passed':
                    count_pass += 1
                else:
                    count_fail +=1
        return count_pass, count_fail

    def htmlFileConvertion(self, testCaseJsonFilePath, tfsQueryResultJsonFilePath, sampleHTMLFilePath,
                               HTMLReportFilePath):
        print('Generate HTML File - Inprogress')
        m_list = []
        query_list = []
        m_dict = {}

        jsonFile = self.read_json_file(testCaseJsonFilePath)
        query_file = self.read_json_file(tfsQueryResultJsonFilePath)
        headFilLoc = os.getcwd().replace('\\','/') + '/header.json'
        header_name = open(headFilLoc,'r')
        header_name = json.load(header_name)

        for i in query_file:
            query_list.append(i)

        for items in jsonFile["Suites"]:
            for k,v in items.iteritems():
                  if k =="testcases":
                    for i in v:
                        m_dict = i
                        #print m_dict
                    for key in m_dict:
                        #rint key
                        for k_val in header_name:
                            if key == k_val:
                                #print header_name[k_val]
                                m_list.append(header_name[k_val])
            break

        loader = jinja2.FileSystemLoader(sampleHTMLFilePath)
        env = jinja2.Environment(loader=loader)
        template = env.get_template('')

        html_output = template.render(m_list=m_list, data=jsonFile["Suites"], query_file=query_file,
                                      query_list=query_list, count_p=self.runStatus(jsonFile)[0],
                                      count_f=self.runStatus(jsonFile)[1])

        with open(HTMLReportFilePath, 'w') as fileWrite:
            fileWrite.write(html_output.encode('utf-8'))
            print('Generate HTML File - Completed. File Location: ' + str(HTMLReportFilePath))
        fileWrite.close()
