"""
Description: Deployment Scripts for 2NetPHC
"""

import os
import sys
import traceback

from commands.shellcommands import execute_command
from argparse import ArgumentParser
import urllib3
import yaml
from hsp_cf.cf import CfApi
from hsp_cf.create_manifests import render_manifests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def parse_args():
    """
    Argument parser
    :return:
    """
    parser = ArgumentParser()

    parser.add_argument("CF_API_HOST",
                        help="Provide cf api HOST")
    parser.add_argument("CF_LOGIN_HOST",
                        help="Provide cf login HOST")
    parser.add_argument("CF_ORG",
                        help="Provide cf org")
    parser.add_argument("CF_SPACE",
                        help="Provide cf space")
    parser.add_argument("CF_USERNAME",
                        help="Provide cf user name")
    parser.add_argument("CF_PASSWORD",
                        help="Provide cf password in quotes")
    parser.add_argument("CSV_FILE",
                        help="Provide csv file name")
    parser.add_argument("LOG_LEVEL",
                        help="Provide logging level as info or debug or error")
    parser.add_argument("RELEASE_VERSION",
                        help="provide release version. Example 1.0.0.0")
    return parser.parse_args()


def cf_login_command(cf_api_host,
                     cf_username,
                     cf_password,
                     org_name,
                     space_name):
    """
    Form cf cli command
    :param cf_api_host:
    :param cf_username
    :param cf_password:
    :param org_name:
    :param space_name:
    :return:
    """
    if 'win' in sys.platform:
        command = 'cf login -a ' + "https://" \
                  + str(cf_api_host) + " -u " \
                  + str(cf_username) + " -p " \
                  + str(cf_password) \
                  + " -o " \
                  + str(org_name) + " -s " \
                  + str(space_name)
    else:
        command = 'cf login -a ' + "https://" \
                  + str(cf_api_host) + " -u " \
                  + str(cf_username) + " -p " \
                  + "'" \
                  + str(cf_password) \
                  + "'" \
                  + " -o " \
                  + str(org_name) + " -s " \
                  + str(space_name)

    exit_status = os.system(command)
    if exit_status != 0:
        print ('cf login failed')
        sys.exit(1)

def generate_manifest():
    """
    Generate Manifest
    :return:
    """
    try:
        print ('')
        print ("########## Creation of Application Manifest started ##########")
        input_folder = TEMPLATE_PATH
        template_names = os.listdir(input_folder)
        output_folder = MANIFEST_PATH + '/'
        render_manifests(config_file,
                         template_names,
                         input_folder,
                         output_folder)
        print ("********** Creation of Application Manifest is completed")
    except Exception as _e1:
        print (_e1.message)


def read_yaml(config_file):
    """
    Read yaml
    :param config_file:
    :return:
    """
    try:
        with open(config_file) as _f:
            configurations = yaml.load(_f.read(), Loader=yaml.FullLoader)
            return configurations
    except IOError as _e:
        print ("I/O error({0}): {1}".format(_e.errno, _e.strerror))
        sys.exit(1)

def deploy(args):
    """
    Main module
    :return:
    """

    print ('Generate Manifest file')
    generate_manifest()
    print ('')

    print ("########## CF Deployment is started: Random Number ##########")
    app_deploy_cmd = ["cf", "push", "-f", "manifests/01_randomnumber.yml"]

    print ("Deployment logs will be displayed shortly")
    exit_status, command_output = execute_command(app_deploy_cmd)
    print (command_output.strip())

    if exit_status == 0:
        print ("********** Random Number App is deployed successfully")
    else:
        sys.exit(1)

    print ("########## CF Deployment is started: Greet User ##########")
    app_deploy_cmd = ["cf", "push", "-f", "manifests/02_greetuser.yml"]

    print ("Deployment logs will be displayed shortly")
    exit_status, command_output = execute_command(app_deploy_cmd)
    print (command_output.strip())

    if exit_status == 0:
        print ("********** Greet User App is deployed successfully")
    else:
        sys.exit(1)

    print ('')

    print ("########## Smoke Test Execution is started ##########")
    input_file = args.CSV_FILE
    try:
        log_level = args.LOG_LEVEL
    except IndexError:
        log_level = None

    log_level_array = ["info", "debug", "error", "warning"]
    if log_level is None or log_level not in log_level_array:
        log_level = "info"

    release_version = args.RELEASE_VERSION
    smoke_test_cmd = ["python", "smoketest/driver.py", input_file, log_level, release_version]
    exit_status, command_output = execute_command(smoke_test_cmd)
    print (command_output.strip())
    if exit_status == 0:
        print ("********** Smoke Test Execution is successfully")
    else:
        print ("********** Smoke Test Execution is failed")
        sys.exit(1)

if __name__ == '__main__':
    TEMPLATE_PATH = './templates'
    MANIFEST_PATH = './manifests'

    try:
        ARGS = parse_args()
    except Exception as _e:
        print (_e.message)

    try:
        CF_LOGIN_HOST = ARGS.CF_LOGIN_HOST
        CF_API_HOST = ARGS.CF_API_HOST
    except KeyError as _e:
        print ("Following key is missing:{0}" .format(_e.message))
        traceback.print_exc()
        sys.exit(1)

    try:
        CF_API = CfApi(username=ARGS.CF_USERNAME,
                       password=ARGS.CF_PASSWORD,
                       login_host=CF_LOGIN_HOST,
                       api_host=CF_API_HOST,
                       org_name=ARGS.CF_ORG,
                       space_name=ARGS.CF_SPACE)
    except:
        print ('cf api object initialization failed')
        print (traceback.print_exc())
        sys.exit(1)

    try:
        cf_login_command(CF_API_HOST,
                         ARGS.CF_USERNAME,
                         ARGS.CF_PASSWORD,
                         ARGS.CF_ORG,
                         ARGS.CF_SPACE)
       
        print ('')
        print ('------ Generate Manifest files and Deploy in CF ------')
        config_file = os.path.join(os.getcwd(), 'configurations', 'deployment-config.yaml')

        deploy(ARGS)
        print ('')

        print ('########## Direct Deployment is completed ##########')
    except KeyError as _e:
        print ("Following key is missing:{0}".format(_e.message))
        traceback.print_exc()
        sys.exit(1)
    except:
        print ('')
        print ('########## Direct Deployment is failed ##########')
        traceback.print_exc()
        sys.exit(1)
