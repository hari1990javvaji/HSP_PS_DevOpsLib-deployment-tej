

from smoketest.lib.utility import Utility
#from smoketest.lib.vault.TestConfig import TestConfig
#TestConfig = TestConfig()

UTILITY_TEST = Utility()


class JavaUtil(object):

    def __init__(self):
        self.step_status = 'FAILED'
        self.actual_verified_comment = 'Step Did Not Verify'
        self.url = 'NA'

    def XXXXXXXXXXXXXX(self, vault_path, tc_log):
        rtn_val = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        if rtn_val.lower() == 'true':
            self.actual_verified_comment = 'Config file is downloaded from Vault'
            self.step_status = 'Passed'
        else:
            self.actual_verified_comment = 'Config file did not download from vault'
            self.step_status = 'Failed'
        list = []
        list.extend([self.url, self.actual_verified_comment, self.step_status])
        return list

    def YYYYYYYYYYYYYYYYYY(self, tc_log):
        rtn_val = 'YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY'
        if rtn_val.lower() == 'true':
            self.actual_verified_comment = 'Config file is deleted in the local location'
            self.step_status = 'Passed'
        else:
            self.actual_verified_comment = 'Config file did not delete'
            self.step_status = 'Failed'
        list = []
        list.extend([self.url, self.actual_verified_comment, self.step_status])
        return list
