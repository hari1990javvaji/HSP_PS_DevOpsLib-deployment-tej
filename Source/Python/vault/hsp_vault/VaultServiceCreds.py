#! /usr/bin/python
"""Vault Service Creds script to get service credentials"""
import subprocess
import os
import sys
import json
from cloudfoundry_client.client import CloudFoundryClient


def get_space_guid(client, cf_org, cf_space):
    """ Method to get CF Space guid.

    :param client: Cloud foundry client for Vault
    :param cf_org: CF Org Name
    :param cf_space: CF Space Name
    :return: Returns Space guid
    """

    for organization in client.organizations:
        if str(organization['entity']['name']).lower() == str(cf_org).lower():
            for spaces in organization.spaces():
                if str(spaces['entity']['name']).lower() == str(cf_space).lower():
                    return spaces['metadata']['guid']


def get_service_guid(client, space_guid, vault_service_name):
    """ Method to get CF Vault Service Name guid.

    :param client: Cloud foundry client for Vault
    :param space_guid: CF Space guid
    :param vault_service_name: CF Vault Service Name
    :return: Returns Service Instance guid
    """

    print(client.service_instances)
    for service in client.service_instances:
        if space_guid is not None and vault_service_name != '':
            if service['entity']['space_guid'] == space_guid and \
                    str(service['entity']['name']).lower() == str(vault_service_name).lower():
                return service['metadata']['guid']
        elif space_guid is None and vault_service_name != '':
            if str(service['entity']['name']).lower() == str(vault_service_name).lower():
                return service['metadata']['guid']
        else:
            print('Input: Vault Service Name is empty.')
            break
    return None


def get_service_key_creds(client, service_guid):
    """ Method to get the Service Key based on vault service name guid .

    :param client: Cloud foundry client for Vault
    :param service_guid: CF Vault Service guid
    :return: Returns Service Key object
    """

    if service_guid is not None:
        for service_key in client.service_keys:
            if service_key['entity']['service_instance_guid'] == service_guid.strip():
                return service_key['entity']['credentials']
    else:
        print('Service guid is empty.')
    return None


def get_vault_service_credentials(cf_url,
                                  cf_user_name,
                                  cf_password,
                                  cf_org,
                                  cf_space,
                                  vault_service_name,
                                  command_type=None):
    """ get_vault_service_credentials: Method to get Service-Key.
    :param cf_url: Cloud Foundry URL.
    :param cf_user_name: Cloud Foundry UserName.
    :param cf_password: Cloud Foundry Password
    :param cf_org: Cloud Foundry Org
    :param cf_space: Cloud Foundry Space
    :param vault_service_name: Cloud Foundry Vault Service Instance Name
    :param command_type:
    :return: Returns client for Vault
    Note: Do not print to print any information
    """
    try:
        if command_type != 'cf_client':
            get_vault_creds = cf_cli_get_key(cf_url,
                                             cf_user_name,
                                             cf_password,
                                             cf_org,
                                             cf_space,
                                             vault_service_name)
            return get_vault_creds

        get_vault_creds = cf_get_key(cf_url,
                                     cf_user_name,
                                     cf_password,
                                     cf_org,
                                     cf_space,
                                     vault_service_name)
        return get_vault_creds

    except Exception as e:
        print("Failed to get vault_service_credentials")
        print(e)


def cf_cli_get_key(cf_url,
                   cf_user_name,
                   cf_password,
                   cf_org,
                   cf_space,
                   vault_service_name):
    """ Method to get Service-Key through commandline.

    :param cf_url: Cloud Foundry URL.
    :param cf_user_name: Cloud Foundry UserName.
    :param cf_password: Cloud Foundry Password
    :param cf_org: Cloud Foundry Org
    :param cf_space: Cloud Foundry Space
    :param vault_service_name: Cloud Foundry Vault Service Instance Name
    :return: Returns client for Vault
    """
    response, status = cf_cli_login(cf_url, cf_user_name, cf_password, cf_org, cf_space)
    get_vault_keys = None
    if status is True:
        print('Logged in to Cloud Foundry')
        vault_service_key = '{}-service-key'.format(vault_service_name)
        try:
            if is_service_exists(vault_service_name) is True:
                create_service_key(vault_service_name, vault_service_key)
                get_vault_keys = get_service_key_credentials(vault_service_name, vault_service_key)
        except Exception as e:
            print("we have hit an exception in get_vault_service_credentials")
            print(e)
    else:
        print('Failed to login to cloud foundry')
        sys.exit(1)
    return get_vault_keys


def cf_get_key(cf_url,
               cf_user_name,
               cf_password,
               cf_org,
               cf_space,
               vault_service_name, ):
    """ Method to get Service-Key through cf api.

    :param cf_url: Cloud Foundry URL.
    :param cf_user_name: Cloud Foundry UserName.
    :param cf_password: Cloud Foundry Password
    :param cf_org: Cloud Foundry Org
    :param cf_space: Cloud Foundry Space
    :param vault_service_name: Cloud Foundry Vault Service Instance Name
    :return: Returns client for Vault
    """
    try:
        http = os.environ.get('http_proxy')
        if len(http) == 0:
            http = os.environ.get('http_proxy', '')
    except:
        print("Environment Variable Did Not Exist: HTTP_PROXY. Setting Value as Blank")
        http = os.environ.get('http_proxy', '')
    try:
        https = os.environ.get('https_proxy')
        if len(https) == 0:
            https = os.environ.get('https_proxy', '')
    except:
        print("Environment Variable Did Not Exist: HTTPS_PROXY. Setting Value as Blank")
        https = os.environ.get('https_proxy', '')

    proxy = dict(http=http, https=https)
    client = CloudFoundryClient(cf_url, proxy=proxy, skip_verification=True)
    client.init_with_user_credentials(cf_user_name, cf_password)
    keys = None

    if cf_org != '' and cf_space != '':
        space_guid = get_space_guid(client, cf_org, cf_space)
        if space_guid is not None:
            service_guid = get_service_guid(client, space_guid, vault_service_name)
            if service_guid is not None:
                keys = get_service_key_creds(client, service_guid)
    else:
        print('Input: Org or Space is empty. Considering by default, Space guid is empty')
    return keys


def execute_command(command):
    """
    execute_command:Execute the provided command in shell
    :param command:
    :return: response, status
    """
    try:
        http = os.environ.get('HTTP_PROXY')
        if len(http) == 0:
            http = os.environ.get('HTTP_PROXY', '')
    except:
        http = ''

    try:
        https = os.environ.get('HTTPS_PROXY')
        if len(https) == 0:
            https = os.environ.get('HTTPS_PROXY', '')
    except:
        https = ''

    proxy = dict(os.environ)
    proxy['HTTP_PROXY'] = http
    proxy['HTTPS_PROXY'] = https
    response = (subprocess.Popen(command,
                                 shell=False, stdout=subprocess.PIPE,
                                 env=proxy).communicate()[0]).decode().lower()
    index = response.find('failed\n')
    status = False
    if index == -1:
        status = True
    return response, status


def cf_cli_login(cf_url, cf_user_name, cf_password, cf_org, cf_space):
    """cf_cli_login: Attempts CF login with given user name and password.
    WARNING: DO NOT CALL THIS WITH INVALID CREDENTIALS
    :param cf_url: CF API Host Name. Example: api.cloud.pcftest.com
    :param cf_user_name: CF user id
    :param cf_password: CF password
    :param cf_org: CF org
    :param cf_space: CF Space
    :return: execute_command(command)
    """

    command = ["cf", "login", "-a", cf_url,
               "-u", cf_user_name,
               "-p", cf_password,
               "-o", cf_org,
               "-s", cf_space]

    return execute_command(command)


def create_service_key(vault_service_name, service_key):
    """create_service_key:Create the service key for a given service
        :param vault_service_name:Cloud Foundry Vault Service Instance Name
        :param service_key:
        :return: status
    """

    command = ['cf', 'create-service-key', vault_service_name, service_key]
    response, status = execute_command(command)

    if status is False and 'not found' in response:
        return status
    if not status:
        print("Failed to create service key for provided service instance {vault_service_name}"
              "\n\t\t\tError: " + response)
    return status


def get_service_key_credentials(vault_service_name, service_key):
    """get_service_key_credentials:Return the credentials for the given service
        :param vault_service_name:Cloud Foundry Vault Service Instance Name
        :param service_key:
        :return: status
    """

    command = ['cf', 'service-key', vault_service_name, service_key]
    response, status = execute_command(command)
    if not status:
        print('Failed to get service key. Please check service exists. response:' + response)
        return None
    response = response.split('\n')[1:]
    response = ''.join(response)
    return json.loads(response.strip())


def is_service_exists(vault_service_name):
    """is_service_exists: Check service exists in the CF
        :param vault_service_name:Cloud Foundry Vault Service Instance Name
        :return: Returns if service exist or not
    """
    command = ['cf', 'service', vault_service_name]
    response, success = execute_command(command)
    if 'failed' in response.lower():
        print('Vault Service Did Not Exist')
        return False
    return True


def exit_if_error(output):
    """ exit_if_error: Check if output contains string OK if not,exit
    :param output: Output
    :return: None
    """
    if 'OK' not in output:
        sys.exit(1)
