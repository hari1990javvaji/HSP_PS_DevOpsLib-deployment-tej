import os
import sys
import yaml
import json
import traceback
from argparse import ArgumentParser


def main(ps_name, domain, docker_username, docker_registry_image_path, log_service_name):
    """This function reads the cofig-core.yaml file and add/update the key value pairs"""

    config_file = os.path.join(os.getcwd(), 'configurations', 'deployment-config.yaml')
    try:
        with open(config_file) as yml_file_read:
            configs = yaml.full_load(yml_file_read.read())

            configs['common_configurations']['docker_user'] = docker_username
            configs['common_configurations']['domain'] = domain
            configs['common_configurations']['log_service_name'] = log_service_name
            configs['apps']['phc']['app_attributes']['name'] = ps_name
            configs['apps']['phc']['app_attributes']['host'] = ps_name
            configs['apps']['phc']['app_attributes']['docker_image'] = docker_registry_image_path

            with open(config_file, 'w') as yml_file_write:
                yaml.dump(configs, yml_file_write)

    except IOError:
        print(("ERROR: Can't read config from {0}".format(config_file)))
        traceback.print_exc()
        sys.exit(1)
