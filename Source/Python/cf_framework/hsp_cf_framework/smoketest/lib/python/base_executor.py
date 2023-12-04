"""
# File Name:        custom_python.py
# Description:    This library is used to manage the custom flow
# Created By:        
"""

import json
import logging


class PythonBaseExecutor(object):

    def base_executor_flow(self, step_obj, tc_log):
        input_data = json.loads(step_obj['InputData'])
        method_name = input_data['METHOD']
        list = []
        try:
            print('Example. Method Name', method_name)
            logging.info('Example. Method Name', method_name)
            tc_log.info('Example. Method Name', method_name)

            '''
            if method_name == 'XXXXXXXX':               			
                vault_path = input_data['VAULT_PATH']
                logging.debug('Vault Path: ' + vault_path)
                return VaultUtilTest.get_vault_config(vault_path, tc_log)
            elif method_name == 'delete_vault_config':
                return VaultUtilTest.delete_vault_config(tc_log)
            '''
        except:
            list.extend(['NA', 'Did not verify. Check Custom Method', 'Failed'])
            return list
