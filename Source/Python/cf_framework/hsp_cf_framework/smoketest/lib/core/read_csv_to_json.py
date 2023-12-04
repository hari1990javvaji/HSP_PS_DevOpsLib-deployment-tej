"""
read csv file to json
"""

import csv
import json


class CsvToJson(object):
    """
    CSV to JSON Class
    """

    def __init__(self):
        self.store = []
        self.segment = {}
        self.tc_name = None

    def csv_reader(self, csv_file, out_file):
        """ Reads CSV file and converts to s json file
        :param csv_file: Input CSV file name or path
        :return: None but It creates a file
        """
        test_case_lst = dict()
        test_case_lst['TestCases'] = []

        csv_file = open(csv_file, 'r')
        csv_reader = csv.DictReader(csv_file, fieldnames=("TC_EXEC_FLAG", "TC_TYPE", "TC_UNIQUE_ID", "TC_NAME",
                                                          "TC_STEP_EXEC_FLAG", "TC_STEP_NAME", "METHOD", "INPUT_DATA",
                                                          "RUNTIME_DATA", "RUNTIME_CUSTOM_SCRIPT", "TC_OR_STEP_DELAY_TIME",
                                                          "EXPECTED_DATA", "EXPECTED_CUSTOM_SCRIPT", "DATA_DRIVEN"))

        next(csv_reader)
        for row in csv_reader:
            # creates the frame for the json
            frame = {"TestExecFlag": row["TC_EXEC_FLAG"],
                     "TestUniqueID": row["TC_UNIQUE_ID"],
                     "TestName": row["TC_NAME"],
                     "TestType": row["TC_TYPE"],
                     "TestDelayTime": row["TC_OR_STEP_DELAY_TIME"],
                     "Steps": []}
            if row['TC_EXEC_FLAG'] != '':
                self.store.append(frame)

            # appends the steps in the json
            if row['TC_EXEC_FLAG'] is not None:
                if row['TC_NAME'] != '':
                    self.tc_name = row['TC_NAME']
                if row['TC_STEP_EXEC_FLAG'] != '':
                    self.segment = {
                        "TestStepExecFlag": row["TC_STEP_EXEC_FLAG"],
                        "TestStepName": row["TC_STEP_NAME"],
                        "Method": row["METHOD"],
                        "InputData": row["INPUT_DATA"],
                        "RunTimeData": row["RUNTIME_DATA"],
                        "RunTimeCustomScript": row["RUNTIME_CUSTOM_SCRIPT"],
                        "TestStepDelay": row["TC_OR_STEP_DELAY_TIME"],
                        "ExpectedData": row["EXPECTED_DATA"],
                        "ExpectedCustomScript": row["EXPECTED_CUSTOM_SCRIPT"],
                        "DataDriven": row["DATA_DRIVEN"]}

                    for i in range(len(self.store)):
                        if self.store[i]['TestName'] == self.tc_name:
                            self.store[i]['Steps'].append(self.segment)

        test_case_lst = []
        test_case_lst.append({
            "TestCases": self.store
        })

        with open(out_file, 'w') as file_object:
            json.dump(test_case_lst[0], file_object, indent=4)
        self.store = []
