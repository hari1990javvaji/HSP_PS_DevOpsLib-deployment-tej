"""
@author : Sirisha
"""

import json
import logging
import os


class JsonMerger(object):

    def jsonObject(selfself, file):
        """Loads the json file into an object"""
        file = open(file, "r")
        jsonObj = json.load(file)
        return jsonObj

    def jsonMerge(self,head_file,*args):
        """
        will take two parameters as file, and append one file to another
        and returns ths updated json object.
        """
        self.head_file = self.jsonObject(head_file)
        self.jsonList1 =  self.head_file["TestCases"]
        #print self.head_file
        file_list = []
        for file in args:
           file_dict = self.jsonObject(file)
           file_list.append(file_dict)

        for items in file_list:
            for i in items['TestCases']:
                self.head_file["TestCases"].append(i)
        return self.head_file

    def jsonMergeArray(self,files):
        """
        will take an array parameters as list of file and append one file to another
        and returns ths updated json object.
        """

        head_file = self.jsonObject(files[0])
        self.jsonList1 =  head_file["TestCases"]
        file_list = []
        for file in files:
            if file !=files[0]:
                file_dict = self.jsonObject(file)
                file_list.append(file_dict)

        for items in file_list:
            for i in items['TestCases']:
                head_file["TestCases"].append(i)
        return head_file
