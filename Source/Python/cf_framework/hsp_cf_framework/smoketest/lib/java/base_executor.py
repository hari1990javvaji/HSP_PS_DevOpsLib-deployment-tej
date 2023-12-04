"""
# File Name:        custom_python.py
# Description:    This library is used to manage the custom flow
# Created By:        
"""

import json
#from smoketest.lib.java.java_util import JavaUtil


class JavaBaseExecutor(object):

    def base_executor_flow(self, step_obj, tc_log):
        input_data = json.loads(step_obj['InputData'])
        method_name = input_data['METHOD']
        if method_name == '':
            print('Example')
            #return JavaUtil.XXXXXXXXXXXXXXX
        elif method_name == 'delete_vault_config':
            print('Example')
            #return JavaUtil.XXXXXXXXXXXXXXX
