"""
# File Name:    rest.py
# Description:  This library is used to manage the execution flow
# Created By:   Tejeswara Rao Kottapalli
"""

import json
import logging
from lib.rest.headers import Headers
from lib.rest.base_runtime_custom import BaseRuntimeCustom
from lib.rest.base_expected_custom import BaseExpectedCustom
from lib.utility import Utility
HEADERS_GEN = Headers()
BASE_RUNTIME_CUSTOM_TEST = BaseRuntimeCustom()
BASE_EXPECTED_CUSTOM_TEST = BaseExpectedCustom()
UTILITY_TEST = Utility()


class RestBaseExecutor(object):
    """
    Class object for Verifying Rest Request Flow
    """

    def __init__(self):
        pass

    def workflow(self, input_object, file_dir, step_log):
        """
        :param input_object: Input Object from Csv File/Json Object
        :return: NA
        """



        rest_input = json.loads(input_object['InputData'])

        rest_url = rest_input['URL']
        rest_payload = rest_input['PAYLOAD']
        rest_header = rest_input['HEADER']
        rest_cert = rest_input.get('CERTIFICATE', '')

        # Update REST URL with all parameters
        step_log.info(' ******** Rest URL ******** ')
        rest_url_updated = UTILITY_TEST.update_parameter_values(rest_url)
        logging.info('REST URL: ' + rest_url_updated)
        step_log.info('REST URL: ' + rest_url_updated)

        # Update Request Body with all parameters
        step_log.debug(' ******** Request Body ******** ')
        test_data_loc = file_dir + '/datasource'
        rest_payload_updated = self.build_payload(test_data_loc, rest_payload)
        step_log.debug('PAYLOAD:  ' + str(rest_payload_updated))
        logging.debug('PAYLOAD: ' + str(rest_payload_updated))

        # Building Headers
        step_log.debug(' ******** Headers ******** ')
        headers = {}
        if rest_header != '':
            header_method = ((UTILITY_TEST.find_parameters_list(rest_header))[1])[0]
            headers = HEADERS_GEN.GenerateHeaders(header_method)
        step_log.debug('Header: ' + str(headers))
        logging.debug('Header: ' + str(headers))

        # Performing Rest Request Operation
        step_log.info(' ******** Performing Rest Request Operation ******** ')
        expected_data = json.loads(input_object['ExpectedData'])
        status_code = expected_data['STATUS_CODE']

        rest_method = input_object['Method']

        response_obj = UTILITY_TEST.send_api_request(rest_method,
                                                     rest_url_updated,
                                                     rest_payload_updated,
                                                     headers, rest_cert, status_code)

        step_log.info(' ******** Response ******** ')

        logging.info('Response: ' + str(response_obj))
        step_log.info('Response: ' + str(response_obj))

        actual_verified_comment = ''
        step_status = 'Failed'
        if response_obj[0] != 'REQUEST FAILED':
            step_log.debug(response_obj[0].text)

            # Get Runtime Values from Response and Store in config.properties file
            self.store_runtime_values(input_object, response_obj, step_log)

            # Verifying Response - Verifying against expected and also custom expected data.
            expected_response_status = self.verify_expected_response(input_object, response_obj)
            step_log.debug('---------VERIFIFY EXPECTED CUSTOM RESPONSE------------------')
            expected_custom_response_status = self.verify_expected_custom_response(input_object, response_obj, step_log)
            if expected_response_status[0].lower() == 'true' and expected_custom_response_status[0].lower() == 'true':
                if expected_response_status[1].lower() == 'passed' and \
                        expected_custom_response_status[1].lower() == 'passed':
                    step_status = 'Passed'
                actual_verified_comment = expected_response_status[2] + ' ' + expected_custom_response_status[2]
            elif expected_response_status[0].lower() == 'true' and \
                    expected_custom_response_status[0].lower() == 'false':
                if expected_response_status[1].lower() == 'passed':
                    step_status = 'Passed'
                actual_verified_comment = expected_response_status[2]
            elif expected_response_status[0].lower() == 'false' and \
                    expected_custom_response_status[0].lower() == 'true':
                if expected_custom_response_status[1].lower() == 'passed':
                    step_status = 'Passed'
                actual_verified_comment = expected_custom_response_status[2]
            elif expected_response_status[0].lower() == 'false' and \
                    expected_custom_response_status[0].lower() == 'false':
                actual_verified_comment = 'Did not verify since expected data is empty.'
                step_log.info(actual_verified_comment)
        else:
            actual_verified_comment = 'Rest Request is failed. Check Proxy details and try.'
            step_log.error('Rest Request is failed. Check Proxy details and try.')

        list = []
        list.extend([rest_url_updated, actual_verified_comment, step_status, response_obj[2]])
        return list

    def build_payload(self, src_dir, file_name):
        """
        :param src_dir: Folder path of the file
        :param file_name: File Name
        :return: Returns uploaded payload object
        """

        rtn_obj = ''
        if file_name != '':
            rtn = UTILITY_TEST.find_parameters_list(file_name)
            if int(rtn[0]) == 1:
                file_exist = UTILITY_TEST.get_file_name_extension((rtn[1])[0])
                if file_exist[1] != '':
                    copy_payload_obj = UTILITY_TEST.read_file(src_dir + '/' + (rtn[1])[0])
                    rtn_obj = UTILITY_TEST.update_parameter_values(copy_payload_obj)
        else:
            rtn_obj = file_name
        return rtn_obj

    def store_runtime_values(self, input_object, response_obj, step_log):
        """
        :param input_object: Input Key values (Json file)
        :param response_obj: Rest Response Object
        :return: NA
        """

        if input_object.get('RunTimeData', '') != '':

            expected_runtime_data = json.loads(input_object['RunTimeData'])
            if expected_runtime_data.get('RESP_BODY_GET', '') != '':
                logging.debug(expected_runtime_data['RESP_BODY_GET'])
                UTILITY_TEST.update_prop_from_response('config.properties',
                                                       response_obj[0].text,
                                                       expected_runtime_data['RESP_BODY_GET'])

            elif expected_runtime_data.get('RESP_BODY_JSON_PARSE', '') != '':
                logging.debug(expected_runtime_data['RESP_BODY_JSON_PARSE'])
                UTILITY_TEST.update_prop_from_response_jsonpath('config.properties',
                                                                response_obj[0].text,
                                                                expected_runtime_data['RESP_BODY_JSON_PARSE'])

            elif expected_runtime_data.get('RESP_HEADER_GET', '') != '':
                logging.debug(expected_runtime_data['RESP_HEADER_GET'])
                UTILITY_TEST.update_prop_from_response_header('config.properties',
                                                                response_obj[0].headers,
                                                                expected_runtime_data['RESP_HEADER_GET'])

        if input_object.get('RunTimeCustomScript', '') != '':
            expected_runtime_custom_data = json.loads(input_object['RunTimeCustomScript'])
            BASE_RUNTIME_CUSTOM_TEST.runtime_custom_script(expected_runtime_custom_data, response_obj, step_log)

    def verify_expected_response(self, input_object, response_obj):
        """
        :param input_object: Input Key values (Json file)
        :param response_obj: Rest Response Object
        :return: It returns 3 values, Expected Flag, Status of the verification and Verified content
        """

        expected_data_flag = 'False'
        status_code_comment = ''
        response_status_comment = ''
        status = 'Passed'
        if input_object.get('ExpectedData', '') != '':
            expected_data_flag = 'True'
            expected_data = json.loads(input_object['ExpectedData'])

            status_code_verify = 'True'
            if expected_data.get('STATUS_CODE', '') != '':
                if int(expected_data['STATUS_CODE']) == int(response_obj[0].status_code):
                    status_code_comment = 'Verified Status Code: ' + str(response_obj[0].status_code)
                else:
                    status_code_comment = 'Did Not Verify Status Code: ' + str(response_obj[0].status_code)
                    status_code_verify = 'False'

            response_status_verify = 'True'
            if expected_data.get('RESP_BODY_GET', '') != '':
                result = UTILITY_TEST.VerifyResponse(response_obj[0].text, expected_data['RESP_BODY_GET'])
                if result[0] == 'True':
                    response_status_comment = 'Verification is Successful. Verified Text: ' + result[1]
                else:
                    response_status_comment = 'Verification is Unsuccessful. Verified Text: ' + result[1] + \
                                              ' Not Verified Text: ' + result[2]
                    response_status_verify = 'False'

            if status_code_verify == 'False' or response_status_verify == 'False':
                status = 'Failed'

        verified_result_comment = status_code_comment + '\n' + response_status_comment
        return expected_data_flag, status, verified_result_comment

    def verify_expected_custom_response(self, input_object, response_obj, step_log):
        """
        :param input_object: Input Key values (Json file)
        :param response_obj: Rest Response Object
        :return: It returns 3 values, Expected Flag, Status of the verification and Verified content
        """

        expected_custom_data_flag = 'False'
        status = 'FAILED'
        custom_result_comment = 'Expected Custom Method is Failed.'
        if input_object.get('ExpectedCustomScript', '') != '':
            expected_custom_data_flag = 'True'
            expected_custom_data = json.loads(input_object['ExpectedCustomScript'])
            try:
                custom_result_verify = BASE_EXPECTED_CUSTOM_TEST.expected_custom_script(input_object, expected_custom_data, response_obj, step_log)
                status = custom_result_verify[0]
                custom_result_comment = custom_result_verify[1]
            except:
                logging.error('Expected_custom_response verification is Failed')
        return expected_custom_data_flag, status, custom_result_comment
