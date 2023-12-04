'''
############################################################################
#Description : Methods generated for Read/write/update json files
#Author      : Sirisha
#Modified by :
#Comments    :
############################################################################
'''

import json
import logging
from lib.core.json_merge import JsonMerger as JM
from six import iteritems
from builtins import range

class JsonReadWrite(object):
    def __init__(self, **kwargs):
        self.suite_id_list = []
        self.tc_id_list = []
        self.tc_details = {}
        self.m_data = {}
        self.suite_id = kwargs.get("suite_id", None)
        self.tc_id = kwargs.get("tc_id", None)
        if kwargs is not None:
            for (self.k, self.v) in iteritems(kwargs):
                #print "%s == %s" % (self.k, self.v)
                logging.debug("%s == %s" % (self.k, self.v))

    def search_key(self, data, suite_id=None):

        if suite_id is not None:
            self.suite_id = suite_id
        #print self.suite_id
        if isinstance(data, dict):
            #print 'Inside it'
            data_keys = list(data.keys())
            for i in range(len(data_keys)):
                # print data[data_keys[i]]
                if data[data_keys[i]] == self.suite_id:
                    # print "current data",data
                    data_key = list(data.keys())
                    self.m_data = data[data_key[1]]
                    return self.m_data
                    # self.search_key(data[data_key[0]])
                else:
                    self.search_key(data[data_keys[i]])
        elif isinstance(data, list):
            for i in range(len(data)):
                list_keys = data[i]
                if list_keys == self.suite_id:
                    #print "found in list"
                    logging.debug("found in list")
                    break
                else:
                    self.search_key(list_keys)
    """Will retrieve all the suite_id that are present in the json file,
            and will also convert it in string format"""

    def get_suiteId_list(self, data):
        suite_id_list = []
        if isinstance(data, dict):
            data_keys = list(data.keys())
            for i in range(len(data_keys)):
                if data_keys[i] == "TestCaseUniqueID":
                    suite_id_list.append(data[data_keys[i]])
                else:
                    suite_id_list.extend(self.get_suiteId_list(data[data_keys[i]]))
        elif isinstance(data, list):
            for items in data:
                if items == "TestCaseUniqueID":
                    suite_id_list.append(items)
                else:
                    suite_id_list.extend(self.get_suiteId_list(items))
        suite_id_list = [str(items) for items in suite_id_list]
        return suite_id_list

    def get_tc_id(self, suite_id, data):
        self.tc_id_list = []
        '''the below step will return the data structure
            which consists of tc_id for given suite name'''
        self.search_key(data, suite_id)
        if isinstance(self.m_data, list):
            for item in range(len(self.m_data)):
                for key in self.m_data[item].keys():
                    if key == "tcId":
                        self.tc_id_list.append(self.m_data[item][key])
            self.tc_id_list = [str(items) for items in self.tc_id_list]
        elif isinstance(self.m_data, dict):
            for key in self.m_data.keys():
                if key == "tcId":
                    self.tc_id_list.append(self.m_data[key])

        self.tc_id_list = [str(items) for items in self.tc_id_list]
        return self.tc_id_list

    def get_testcase_details(self, data, suite_id, tc_id, *args):
        """This function will return test case details either all or the specified keys"""
        self.search_key(data, suite_id)
        # print self.m_data
        if isinstance(self.m_data, list):
            for k in range(len(self.m_data)):
                for keys in self.m_data[k].keys():
                    # print self.m_data[k][keys]
                    if self.m_data[k][keys] == tc_id:
                        if args:
                            for arg in args:
                                for item in self.m_data[k].keys():
                                    if arg == item:
                                        self.tc_details[arg] = str(self.m_data[k][item])

                        else:
                            return self.m_data[k]
        return self.tc_details

    def json_update(self, data, suite_id, tc_id, **kwargs):
        ''' This function appends/
        updates the json file '''
        suite_data = data
        #print suite_data
        self.search_key(suite_data, suite_id)
        #print self.m_data
        if isinstance(self.m_data, dict):
            print ("hello dict##")
            #logging.debug("hello dict##")
        elif isinstance(self.m_data, list):

            for items in self.m_data:
                index = self.m_data.index(items)
                if isinstance(items, list):
                    pass
                elif isinstance(items, dict):

                    for v in items.values():
                        if v == tc_id:
                            self.l_data = items
                            # print index, self.l_data
                            for (key, val) in iteritems(kwargs):
                                if self.l_data.get(key) is not None:
                                    self.l_data[key] = val
                                    # print "!!",self.l_data
                                elif self.l_data.get(key) is None:
                                    self.l_data[key] = val
                                    # print "@",self.l_data

                            self.m_data[index] = self.l_data
                            # print"update: ", self.m_data
                            break

        """for i in suite_data:
            print "suite_data:", suite_data
            for j in xrange(len(suite_data[i])):
                if suite_data[i][j]["SuiteID"] == suite_id:
                    print "###",suite_data[i][j]["testcases"]"""
        #print suite_data
        #logging.debug("suite_data: %s"%suite_data)
        return suite_data


    def json_delete(self,json_file,*args):
        """To delete the contents in the json file"""
        try:
            while args is not None:
                for i in args:
                    for items in range(len(json_file["TestCases"])):
                        for list_items in json_file["TestCases"][items]["Steps"]:
                            for keys in list_items.keys():
                                if keys == i:
                                    del list_items[keys]
                break
            return json_file

        except Exception as e :
            print ("Key Not Found!!")


    def update_json_key(self, data, tc_unque_id, **kwargs):
        for i in range(len(data['TestCases'])):
            if data['TestCases'][i]['TestUniqueID'] == tc_unque_id:
                for (key, val) in iteritems(kwargs):
                    if data['TestCases'][i].get(key) is not None:
                        data['TestCases'][i][key] = val
                        # print "!!",self.l_data
                    elif data['TestCases'][i].get(key) is None:
                        data['TestCases'][i][key] = val
                return data
                