"""
# File Name:        rest_util.py
# Description:    This library is used to manage the execution flow
# Created By:        Tejeswara Rao Kottapalli
"""
import sys
import json
import traceback
import ast
import logging
from lib.utility import Utility
UTILITY_TEST = Utility()


class BaseExpectedCustom(object):

    def expected_custom_script(self, input_object, custom_data, response_obj, step_log):
        rest_input = json.loads(input_object['InputData'])
        tc_id = rest_input['TESTCASEID']
        method_name = custom_data['METHOD']
        if method_name == 'verify_discovery_response':
            return self.verify_discovery_response(tc_id, response_obj[0].text, step_log)

    def verify_discovery_response(self, tc_id, response_obj, step_log):
        step_status = 'FAILED'
        assertion_flag = True
        tags = UTILITY_TEST.get_prop_val_by_section('config.properties', 'STATIC', 'service_tags')
        tags_list = ast.literal_eval(tags)
        expected_names_list = []
        expected_tags_list = []
        names = UTILITY_TEST.get_prop_val_by_section('config.properties', 'STATIC', 'service_names')
        names_list = ast.literal_eval(names)
        logging.debug('discovery response----->' + str(response_obj))
        discovery_response = json.loads(response_obj)
        entry = (discovery_response['entry'])
        try:
            if(tc_id == '11001'):
                for i in range(len(entry)):
                    resource = entry[i]['resource']
                    resourceType = resource['resourceType']
                    tag = resource['tag']
                    expected_tags_list.append(tag)
                    name = resource['name']
                    expected_names_list.append(name)
                    actions = resource['actions']
                    assert name != 'Blob Repository'
                    assert name != 'Discovery'
                    assert tag != 'BLR'
                    assert tag != 'DSC'
                    urls = resource['urls']
                    assert resourceType != 'null'
                    assert tag != 'null'
                    assert actions != 'null'
                    assert tag is not None
                    assert actions is not None
                    assert resourceType is not None
                    assert urls != 'null'
                    assert urls is not None
                    assert resourceType == 'Service', 'Expected resourceType is  ' + 'Service'
                    if(name == 'Identity Access Mgmt'):
                        assert set(actions) == set(['login', 'logout'])
                    else:
                        assert set(actions) == set(['reset', 'unprovision'])
                assert 'Identity Access Mgmt' in expected_names_list
                assert 'Provisioning' in expected_names_list
                assert 'IAM' in expected_tags_list
                assert 'PRV' in expected_tags_list
                
                assert set(expected_names_list) == set(['Identity Access Mgmt', 'Provisioning'])
                assert set(expected_tags_list) == set(['IAM', 'PRV'])

            elif(tc_id == '442278'):
                for i in range(len(entry)):
                    resource = entry[i]['resource']
                    resourceType = resource['resourceType']
                    tag = resource['tag']
                    expected_tags_list.append(tag)
                    name = resource['name']
                    expected_names_list.append(name)
                    actions = resource['actions']
                    urls = resource['urls']
                    assert resourceType != 'null'
                    assert tag != 'null'
                    assert actions != 'null'
                    assert tag is not None
                    assert actions is not None
                    assert resourceType is not None
                    assert urls != 'null'
                    assert urls is not None
                    assert resourceType == 'Service', 'Expected resourceType is  ' + 'Service'
                    if(name == "Blob Repository"):
                        assert set(actions) == set(['upload-blob', 'download-blob', 'query-blob', 'create-presigned-url', 'delete-blob'])
                    elif(name == 'Identity Access Mgmt'):
                        assert set(actions) == set(['login', 'logout'])
                    elif(name == 'Discovery'):
                        assert set(actions) == set(['query-services'])
                    else:
                        assert set(actions) == set(['reset', 'unprovision'])
                    
                assert 'Identity Access Mgmt' in expected_names_list
                assert 'Provisioning' in expected_names_list
                assert 'IAM' in expected_tags_list
                assert 'PRV' in expected_tags_list
                assert 'BLR' in expected_tags_list
                assert 'DSC' in expected_tags_list
                assert 'Blob Repository' in expected_names_list
                assert 'Discovery' in expected_names_list
                assert set(expected_tags_list) == set(tags_list)
                assert set(expected_names_list) == set(names_list)
                
            elif(tc_id == '442279'):
                for i in range(len(entry)):
                    resource = entry[i]['resource']
                    resourceType = resource['resourceType']
                    tag = resource['tag']
                    expected_tags_list.append(tag)
                    name = resource['name']
                    expected_names_list.append(name)
                    actions = resource['actions']
                    urls = resource['urls']
                    assert resourceType != 'null'
                    assert tag != 'null'
                    assert actions != 'null'
                    assert tag is not None
                    assert actions is not None
                    assert resourceType is not None
                    assert urls != 'null'
                    assert urls is not None
                    assert resourceType == 'Service', 'Expected resourceType is  ' + 'Service'
                    if(name == "Blob Repository"):
                        assert set(actions) == set(['upload-blob', 'download-blob', 'query-blob', 'create-presigned-url', 'delete-blob'])
                    elif(name == 'Identity Access Mgmt'):
                        assert set(actions) == set(['login', 'logout'])
                    elif(name == 'Discovery'):
                        assert set(actions) == set(['query-services'])
                    else:
                        assert set(actions) == set(['reset', 'unprovision'])
                print('expected_tags_list...', expected_tags_list) 
                assert 'Identity Access Mgmt' in expected_names_list
                assert 'Provisioning' in expected_names_list
                assert 'IAM' in expected_tags_list
                assert 'PRV' in expected_tags_list
                assert 'BLR' in expected_tags_list
                assert 'DSC' in expected_tags_list
                assert 'Blob Repository' in expected_names_list
                assert 'Discovery' in expected_names_list
                assert set(expected_tags_list) == set(tags_list)
                assert set(expected_names_list) == set(names_list)

            else:
                logging.info('No service matches in response')
                
        except KeyError as e:
                _, exc_value, tb = sys.exc_info()
                traceback.print_tb(tb)
                traceback.print_exc()  
                tb_info = traceback.extract_tb(tb)
                filename, line, func, text = tb_info[-1]
                raise KeyError()
                assertion_flag = False
                print('An error occurred on line {} in statement {}'.format(line, text))
                step_log.debug('discovery_response----->' + str(response_obj))
                
        except AssertionError as e:
            _, exc_value, tb = sys.exc_info()
            traceback.print_tb(tb)
            traceback.print_exc()  
            tb_info = traceback.extract_tb(tb)
            filename, line, func, text = tb_info[-1]
            raise AssertionError()
            assertion_flag = False
            print('An error occurred on line {} in statement {}'.format(line, text))
            step_log.debug('discovery_response----->' + str(response_obj))

        except Exception as e:
            _, exc_value, tb = sys.exc_info()
            traceback.print_tb(tb)
            traceback.print_exc()
            tb_info = traceback.extract_tb(tb)
            filename, line, func, text = tb_info[-1]
            raise Exception()
            assertion_flag = False
            print('An error occurred on line {} in statement {}'.format(line, text))
            step_log.debug('discovery_response----->' + str(response_obj))
        
        if assertion_flag:
            step_status = 'PASSED'
            actual_verified_comment = 'Discovery response verification succeeded'
            url = 'NA'
        else:
            step_status = 'FAILED'
            actual_verified_comment = 'Discovery response verification failed'
            url = 'NA'
        list = []
        list.extend([step_status, actual_verified_comment])
        return list
