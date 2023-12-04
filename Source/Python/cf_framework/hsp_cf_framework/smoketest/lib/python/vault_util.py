from smoketest.lib.utility import Utility
#from smoketest.lib.vault.TestConfig import TestConfig
#TestConfig = TestConfig()
UTILITY_TEST = Utility()


class VaultUtil(object):

    def __init__(self):
        self.step_status = 'FAILED'
        self.actual_verified_comment = 'Step Did Not Verify'
        self.url = 'NA'

    def get_vault_config(self, vault_path, tc_log):
        #config_obj = TestConfig.get_file_vault(vault_path)
        rtn_val = UTILITY_TEST.write_to_file('config.properties', config_obj)
        if rtn_val.lower() == 'true':
            actual_verified_comment = 'Config file is downloaded from Vault'
            step_status = 'Passed'
        else:
            actual_verified_comment = 'Config file did not download from vault'
            step_status = 'Failed'
        list = []
        list.extend([self.url, actual_verified_comment, step_status])
        tc_log.info(list)
        return list

    def delete_vault_config(self, tc_log):
        rtn_val = UTILITY_TEST.delete_file('config.properties')
        if rtn_val.lower() == 'true':
            actual_verified_comment = 'Config file is deleted in the local location'
            step_status = 'Passed'
        else:
            actual_verified_comment = 'Config file did not delete'
            step_status = 'Failed'
        list = []
        list.extend([self.url, actual_verified_comment, step_status])
        tc_log.info(list)
        return list