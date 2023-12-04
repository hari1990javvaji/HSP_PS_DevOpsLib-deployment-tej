"""
# File Name:        rest_util.py
# Description:    This library is used to manage the execution flow
# Created By:        Tejeswara Rao Kottapalli
"""

import lib.rest.env_variables
import logging
from lib.utility import Utility
UTILITY_TEST = Utility()


class BaseRuntimeCustom(object):

    def runtime_custom_script(self, custom_data, response_obj, step_log):
        method_name = custom_data['METHOD']
        try:
            if method_name == 'get_transaction_id':
                self.get_transaction_id(response_obj[0].headers, step_log)
        except:
            logging.error('REST API Runtime Custom Method is failed.')

    def get_transaction_id(self, header, step_log):
        transaction_id = header['transactionId']
        logging.debug('Transaction id : ' + str(transaction_id))
        step_log.debug('Transaction id : ' + str(transaction_id))
        if transaction_id != '':
            env_variables.transactionid.append(transaction_id)
            print (env_variables.transactionid)
            transaction_id = env_variables.transactionid

        UTILITY_TEST.add_update_val_in_prop_file_by_section('config.properties',
                                                            'RUNTIME', 'transaction_id', transaction_id)
