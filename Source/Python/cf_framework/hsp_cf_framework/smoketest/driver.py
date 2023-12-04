"""
File Name:   TestDriver.py
Description: File contains Driver method is to read data from CSV or JSON file and then perform various actions
             according to the data sheet
Created By:  Tejeswara Rao Kottapalli
"""

import os
import sys
import json
import time
import datetime
from pytz import timezone
from pathlib import Path
from lib.core.read_csv_to_json import CsvToJson
from lib.core.json_merge import JsonMerger
from lib.core.json_read_write import JsonReadWrite
from lib.rest.base_executor import RestBaseExecutor
from lib.python.base_executor import PythonBaseExecutor
from lib.java.base_executor import JavaBaseExecutor
from lib.utility import Utility
from tabulate import tabulate
import logging
from builtins import range

readJson = CsvToJson()
JsonMergerTest = JsonMerger()
JsonReadWriteTest = JsonReadWrite()
UTILITY_TEST = Utility()
Rest_BaseExecutorTest = RestBaseExecutor()
Python_BaseExecutor = PythonBaseExecutor()
Java_BaseExecutor = JavaBaseExecutor()


class Execution(object):

    def __init__(self):
        pass

    @staticmethod
    def execute_test_case(input_file, log_level):

        total_passed = 0
        total_failed = 0
        start_time = time.time()
        fulltext = ''
        actual_result_location_path = []

        input_dir = os.getcwd().replace('\\', '/') + '/test_data/'
        file_no_ext, ext = os.path.splitext(input_file)
        if ext == '':
            input_dir = input_dir + '/' + file_no_ext
            input_file = ''

        file_lst = UTILITY_TEST.find_file(input_dir, input_file)
        logging.info('')
        logging.info('List of Input CSV Files: ' + str(file_lst))
        if len(file_lst) > 0:
            tc_list = []
            response_time = 0
            for input_file_path in file_lst:
                input_file_with_no_ext = (UTILITY_TEST.get_file_name_extension(os.path.split(input_file_path)[1]))[0]
                file_dir = UTILITY_TEST.moveDirectoryLevelUp(input_file_path, 0).replace('\\', '/')
                file_obj = file_dir + '/' + input_file_with_no_ext + '.json'
                readJson.csv_reader(input_file_path, file_obj)
                json_file = open(file_obj, 'r')
                json_obj = json.load(json_file)
                driver = None
                
                skip_test_execution = ''
                test_cases_count = len(json_obj['TestCases'])
                for i in range(test_cases_count):
                    test_case_details = json_obj['TestCases'][i]
                    exec_status = []
                    tc_status_list = []
                    tc_status = 'NOT RUN'
                    
                    if((test_case_details['TestExecFlag'].lower() == 'yes' or
                        test_case_details['TestExecFlag'].lower() == 'y') and
                            (test_case_details['TestUniqueID'] != skip_test_execution)):
                        logging.info('')
                        logging.info('######################################################################')
                        logging.info('Test Case Name: ' + test_case_details['TestName'])
                        logging.info('Test Case ID: ' + test_case_details['TestUniqueID'])
                        logging.info('')
                        passed = 0
                        failed = 0
                        file_type = UTILITY_TEST.get_file_name_extension(os.path.split(input_file_path)[1])
                        UTILITY_TEST.createDirPath_LongFileDeleteIfExist(os.getcwd().replace('\\', '/')
                                                                         + '/reports/' + file_type[0])
                        tc_log_location = os.getcwd().replace('\\', '/') + '/reports/' + file_type[0] + '/' + \
                                          test_case_details['TestUniqueID'] + '.log'

#                         log_level = UTILITY_TEST.get_prop_value('config.properties', 'log_level')
                        UTILITY_TEST.setup_logger(test_case_details['TestUniqueID'], tc_log_location, log_level)
                        tc_log = logging.getLogger(test_case_details['TestUniqueID'])
                        tc_log.info('Test Case Name: ' + test_case_details['TestName'])
                        fulltext = fulltext + '\n' + \
                                   '-------------------------------------------------' + '\n' + \
                                   'Test Case Name: ' + test_case_details['TestName'] + '\n' + \
                                   '-------------------------------------------------' + '\n'
                        
                        if test_case_details['TestDelayTime'].strip() != '' and \
                                (test_case_details['TestDelayTime'].strip()).isdigit() is True:
                            tc_log.info('Test Case Start Delay in seconds: '
                                        + str(test_case_details['TestDelayTime']))
                            time.sleep(int(test_case_details['TestDelayTime']))
                        
                        for j in range(len(test_case_details['Steps'])):
                            test_steps = test_case_details['Steps'][j]
                            method = test_steps['Method'].lower()
                            if test_steps['TestStepExecFlag'].lower() == 'yes' or \
                                    test_steps['TestStepExecFlag'].lower() == 'y':
                                tc_log.info('----------------------------------------------------------------------')
                                tc_log.info(test_steps['TestStepName'])
                                tc_log.info('----------------------------------------------------------------------')
                                logging.info(' ****** Executing Step: ' + test_steps['TestStepName'])
                                tc_log.info('Executing Step: ' + test_steps['TestStepName'])
                                logging.info('')

                                if test_steps['TestStepDelay'].strip() != '' and \
                                        (test_steps['TestStepDelay'].strip()).isdigit() is True:
                                    tc_log.info('Step Delay in seconds: ' + str(test_steps['TestStepDelay']))
                                    time.sleep(int(test_steps['TestStepDelay']))
                                try:
                                    if method.lower() == 'post' or \
                                            method.lower() == 'get' or \
                                            method.lower() == 'put' or \
                                            method.lower() == 'delete' or \
                                            method.lower() == 'patch':

                                        # Call method (test_steps)
                                        exec_status = Rest_BaseExecutorTest.workflow(test_steps, file_dir, tc_log)
                                        logging.info(exec_status)

                                    elif method.lower() == 'python':
                                        logging.info('Call Python Library')
                                        # Call method (test_steps)
    
                                        step_start_time_python = time.time()
                                        exec_status = Python_BaseExecutor.base_executor_flow(test_steps, tc_log)
                                        logging.info(exec_status)
                                        time.sleep(1)
                                        step_end_time_python = time.time()
                                        step_duration = round((step_end_time_python - step_start_time_python), 5)
                                        logging.info(step_duration)
                                        exec_status.append(str(step_duration))
                                        logging.info(exec_status)
                                    elif method == 'java':
                                        logging.info('Call Java Library')

                                        step_start_time = time.time()
                                        # Call method here (test_steps)
                                        # exec_status = Java_BaseExecutor.base_executor_flow(test_steps, tc_log)
    
                                        step_end_time = time.time()
                                        step_duration = round((step_end_time - step_start_time), 5)
                                        exec_status.append(str(step_duration))
                                        logging.info(exec_status)

                                    updated_json_obj = JsonReadWriteTest.json_update(json_obj,
                                                                                     test_case_details['TestUniqueID'],
                                                                                     test_steps['TestStepName'],
                                                                                     actualComment=exec_status[1],
                                                                                     state=exec_status[2],
                                                                                     Duration=exec_status[3])
                                    with open(file_obj, 'w') as file_object:
                                        json.dump(updated_json_obj, file_object, indent=4)
                                except Exception:
                                    exec_status[2].upper() == 'FAILED'
                                    logging.info('Step Status: ' + exec_status[2])
                                logging.info('')
                                tc_log.info('Step Status: ' + exec_status[2])

                                fulltext = fulltext + '\n' + \
                                           'TEST STEP        : ' + test_steps['TestStepName'] + '\n' + \
                                           'END POINT        : ' + exec_status[0] + '\n' + \
                                           'ACTUAL COMMENT   : ' + exec_status[1] + '\n' + \
                                           'STATUS           : ' + exec_status[2] + '\n' + \
                                           'RESPONSE TIME    : ' + str(exec_status[3]) + '\n'

                                if exec_status[2].upper() == 'PASSED':
                                    passed += 1
                                    total_passed = total_passed + 1
                                elif exec_status[2].upper() == 'FAILED':
                                    failed += 1
                                    total_failed = total_failed + 1

                            else:
                                test_steps = test_case_details['Steps'][j]
                                updated_json_obj = JsonReadWriteTest.json_update(json_obj,
                                                                                 test_case_details['TestUniqueID'],
                                                                                 test_steps['TestStepName'],
                                                                                 actualComment='Not Executed Due to '
                                                                                               'Test Step Execution '
                                                                                               'Flag is not set to '
                                                                                               'either YES/Y/yes/y',
                                                                                 state='NO RUN',
                                                                                 Duration='0.0')
                                with open(file_obj, 'w') as file_object:
                                    json.dump(updated_json_obj, file_object, indent=4)

                                logging.info('')

                        if failed == 0:
                            logging.info(' ****** Test Case Status: Passed')
                            tc_status = 'Passed'
                        else:
                            logging.info(' ****** Test Case Status: Failed')
                            tc_status = 'Failed'

                        updated_json_obj_status = JsonReadWriteTest.update_json_key(json_obj,
                                                          test_case_details['TestUniqueID'],
                                                          state=tc_status, LogLocation=tc_log_location)

                        with open(file_obj, 'w') as file_object:
                            json.dump(updated_json_obj_status, file_object, indent=4)
                          
                    else:
                        tc_status = 'NOT RUN'
                        for j in range(len(test_case_details['Steps'])):
                            test_steps = test_case_details['Steps'][j]
                            updated_json_obj = JsonReadWriteTest.json_update(json_obj,
                                                                             test_case_details['TestUniqueID'],
                                                                             test_steps['TestStepName'],
                                                                             actualComment='Not Executed Due to '
                                                                                           'Test Execution Flag not '
                                                                                           'set to either YES/Y/yes/y',
                                                                             state='NO RUN',
                                                                             Duration='0.0')
                            with open(file_obj, 'w') as file_object:
                                json.dump(updated_json_obj, file_object, indent=4)

                    tc_status_list.extend([test_case_details['TestName'], tc_status.upper()])
                    tc_list.append(tc_status_list)
                    skip_test_execution = UTILITY_TEST.get_prop_val_by_section('config.properties',
                                                                               'STATIC',
                                                                               'skip_test_execution_id')
                end_time = time.time()
                response_time = round((end_time - start_time), 5)

                actual_result_location_path.append(file_obj)

            total_executed = str(int(total_passed) + int(total_failed))
            utc_date = datetime.datetime.now(timezone('UTC')).strftime("%Y-%m-%d %H:%M:%S %Z%z")
            content = fulltext + '\n' + 'EXECUTION TIMESTAMP  : ' + \
                      str(utc_date) + '\n' + 'RELEASE VERSION      : ' + str(sys.argv[3]) + '\n' + '\n' + \
                    '####################################### TEST SUITE SUMMARY ##################################' \
                    '#####' + '\n' + \
                    tabulate(tc_list, headers=['TEST CASE NAME', 'STATUS'], tablefmt='orgtbl') + '\n' + \
                    '\n' + \
                    '######################### EXECUTION SUMMARY ########################################' + '\n' + \
                    '' + \
                    'TOTAL TEST STEPS     : ' + total_executed + '\n' + \
                    'TOTAL STEPS PASSED   : ' + str(total_passed) + '\n' + \
                    'TOTAL STEPS FAILED   : ' + str(total_failed) + '\n' + \
                    'TOTAL EXECUTION TIME : ' + str(response_time)

            logging.info(content)
            file_path = os.getcwd().replace('\\', '/') + '/reports/' + 'Summary.log'
            UTILITY_TEST.write_to_file(file_path.replace('\\', '/'), content)

            if len(actual_result_location_path) > 0:
                '''Merge Multiple Json Files'''
                json_merge_obj = JsonMergerTest.jsonMergeArray(actual_result_location_path)
                with open(os.getcwd().replace('\\', '/') + '/reports/consolidated_execution_report.json', "w") as \
                        file_obj:
                    json.dump(json_merge_obj, file_obj, indent=2)
                    
            if total_failed > 0:
                raise Exception("Test step failed with error")


if __name__ == "__main__":
    os.chdir(str(Path(sys.argv[0]).parents[0]).replace('\\', '/'))
    input_file = sys.argv[1]
    try:
        log_level = sys.argv[2]
    except IndexError:
        log_level = None
    logLevelArray = ["info", "debug", "error", "warning"]
    if log_level is None or log_level not in logLevelArray:
        log_level = "info"

    UTILITY_TEST.logging(os.getcwd(), log_level)
    execute_test = Execution()
    execute_test.execute_test_case(input_file, log_level)
