import os
from smoketest.lib.utility import Utility
utilityLib = Utility()

properties_file_path = os.getcwd().replace('\\', '/') + '/smoketest/config.properties'


def update_smoke_config(app_key, app_val):
    utilityLib.add_update_val_in_prop_file_by_section(properties_file_path, 'APP', app_key, app_val)



