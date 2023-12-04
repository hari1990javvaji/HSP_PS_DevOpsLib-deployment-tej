#!/usr/bin/env python
# pylint: disable=invalid-name
# pylint: disable=logging-not-lazy, logging-format-interpolation
# invalid-name is disabled due to the use of single character variable names
# within context managers and list comprehensions.  Single character
# variables are acceptable in these use cases where the intent is
# clear within a couple of lines of code.
#
# Logging format linting is disable because, .format is recommended in python 3
# and provides readability over interpolation. Interpolation cost is negligible
"""This script should be used to provision all services defined in the
provided configuration file when doing (mostly) automated deployments.
"""
from __future__ import print_function, absolute_import
import argparse
import logging
import sys
import copy
import os
from time import sleep
from six.moves import urllib
import yaml


LOGGER = logging.getLogger('deploy')

CONFIG_FILE_PATH = {
    'repository-path-abs': '/opt/app/cf-deployment'
}


def create_services(cfapi, services):
    """Create service instance in config file.

    Read config file and create service instances using CfApi class.

    Args:
        services (list[dict]): A list of services and service parameters.
        cfapi (CfApi): cf-api instance

    Returns:
        list: A list of services that were created.
    """
    managed = verify_servicename(cfapi, services,
                                 service_type='managed')
    user_provided = verify_servicename(
        cfapi, services, service_type='user-provided'
    )
    existing_services = managed + user_provided

    if existing_services:
        LOGGER.info('Service(s) already exist: '
                    '{0}'.format(', '.join(existing_services)))

    list_of_created_services = []

    for service in list(services.values()):
        try:
            if service['service_name'] not in existing_services:
                if service["service_type"] == 'managed':
                    list_of_created_services = init_managed_services(cfapi, service)
                elif service["service_type"] == 'user-provided':
                    list_of_created_services = init_user_provided_services(cfapi, service)
                else:
                    LOGGER.info("Ignoring service named {0}".format(
                        service['service_name']))
        except urllib.error.HTTPError as err:

            LOGGER.info('Error: {0}'.format(err.read()))
            sys.exit(127)
    return list_of_created_services


def init_managed_services(cfapi, service):
    """initiates creation of managed services

    Read config file and create service instances using CfApi class.

    Args:
        service: A list of services and service parameters.
        cfapi (CfApi): cf-api instance

    Returns:
        list: A list of services that were created.

    """
    list_of_created_services = []
    LOGGER.info("Creating CF service instance: Name: " +
                service['service_name'] + ", Plan: " +
                service['plan_name'] + ", Broker: " +
                service['broker_name'] + '\n')
    service_parameters = {}
    if 'postgres' in service['service_name']:
        service_parameters = get_service_params(service)
    service_parameters = None if not service_parameters else service_parameters
    cfapi.create_service(
        service['service_name'], service['broker_name'],
        service['plan_name'], service_parameters
    )
    list_of_created_services.append(service['service_name'])
    return list_of_created_services


def init_user_provided_services(cfapi, service):
    """initiates creation of managed services

    Read config file and create service instances using CfApi class.

    Args:
        service: A list of services and service parameters.
        cfapi (CfApi): cf-api instance

    Returns:
        list: A list of services that were created.

    """
    list_of_created_services = []
    LOGGER.info("Creating CF user provided service instance:  Name: " +
                service['service_name'] + ' with the default version\n')
    log_drain_url = service.get('syslog_drain_url', None)
    cfapi.create_user_provided_service(
        service['service_name'], service['optional_params'], log_drain_url
    )
    list_of_created_services.append(service['service_name'])
    return list_of_created_services


def get_service_params(service):
    """initiates creation of managed services

    Read config file and create service instances using CfApi class.

    Args:
        service: A list of services and service parameters.

    Returns:
       service_parameters

    """
    service_parameters = {}
    config_params_dict = copy.deepcopy(service['configuration_parameters'])
    for key in list(config_params_dict.keys()):
        if config_params_dict[key] is None:
            del config_params_dict[key]
        elif key == 'database_snapshot':
            if config_params_dict[key]['use_snapshot']:
                print(('Detected snapshot configuration. Creating service instance {0} with'
                       ' snapshot'.format(service['service_name'])))
                del config_params_dict[key]['use_snapshot']
                for k, v in list(config_params_dict[key].items()):
                    service_parameters[k] = v
            else:
                print('Attempting to create postgres instance with allocated storage and version')
                del config_params_dict['database_snapshot']
                service_parameters = config_params_dict
    return service_parameters


def monitor_service_action(cfapi, service_names, action_type, wait_time=15):
    """Works for creation and update of service instances
    Just pass cfapi object and the list of service instance as arguments"""

    status = False
    filters = {'q': 'space_guid:{0}'.format(cfapi.space_guid)}
    minutes_elapsed = 0
    while service_names:
        service_instances = cfapi.service_instances(filters=filters)
        in_progress = check_service_status(action_type, service_instances, service_names)

        if minutes_elapsed > wait_time:
            print(('Wait time exceeded : {} minute. Exiting'.format(wait_time)))
            sys.exit(1)

        if in_progress:
            print(('{1} still in progress for service:{0}'.format(
                ', '.join(list(in_progress.keys())), action_type)))
            print(('Minutes elapsed so far: {}'.format(minutes_elapsed)))
            print('Sleeping for one minute....')
            minutes_elapsed += 1
            sleep(60)
        else:
            print(('{1} performed on service(s) {0}'.format(tuple(service_names), action_type)))
            status = True
            break
    return status


def check_service_status(action_type, service_instances, service_names):
    """Check service creation/updation status

       Args:
           action_type : create or update
               Foundry API calls with.
           service_instances (list[dict]): A list of service dicts with all metadata and
               state for the services.
            service_names: list of service names
       Returns:
           list: A list of in-progress services
       """
    in_progress = {}
    for x in service_instances:
        if x['entity']['last_operation']['state'] != 'succeeded' and \
                x['entity']['last_operation']['type'] == action_type and\
                x['entity']['name'] in service_names:
            in_progress[x['entity']['name']] = x['entity']['last_operation']['state']
            if x['entity']['last_operation']['state'] == 'failed':
                print(str.format("{0} on service instance {1} failed. Exiting", action_type, x["entity"]["name"]))
                sys.exit(1)

    return in_progress


def verify_servicename(cfapi, services, service_type=None):
    """Verify that a existing service does not exist with the same name.

    Args:
        cfapi (cf.CfApi): An instance of the CfApi class to perform Cloud
            Foundry API calls with.
        services (list[dict]): A list of service dicts with all metadata and
            state for the services.

    Returns:
        list: A list of named services that already exist or an empty list.
        :param cfapi:
        :param services:
        :param service_type:
    """
    services = dict([
        (k, v) for (k, v) in list(services.items())
        if v['service_type'] == service_type
    ])
    filters = {'q': 'space_guid:{0}'.format(cfapi.space_guid)}
    if service_type == 'managed':
        service_instances = cfapi.service_instances(filters=filters)
    elif service_type == 'user-provided':
        service_instances = cfapi.user_provided_service_instances(
            filters=filters
        )
    else:
        LOGGER.info('Error: Unknown service type: {0}'.format(service_type))
        sys.exit(127)

    service_names = []
    for v in list(services.values()):
        if type(v) is dict:
            for t, c in list(v.items()):
                if t == 'service_name':
                    service_names.append(c)
    if_exists = [
        s['entity']['name'] for s in service_instances
        if s['entity']['name'] in service_names
    ]
    return if_exists


def parse_args(args=None):
    """Parse command line args.

    Simple function to parse and return command line args.

    Returns:
        argparse.Namespace: An argparse.Namespace object.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-c',
                        '--config',
                        dest='config',
                        default=None,
                        required=True,
                        help='The name of the config file to read service '
                             'parameters from.')
    parser.add_argument('-u',
                        '--cfusername',
                        dest='cfUsername',
                        default=None,
                        required=False,
                        help='Username of the ldap to authenticate...')
    parser.add_argument('-p',
                        '--cfpassword',
                        dest='cfPassword',
                        default=None,
                        required=False,
                        help='Password of the ldap to authenticate...')

    return parser.parse_args(args)


def read_config(path):
    """Reads configuration file

    Simple function to read config file and return it's content

    Returns:
        api_host, config, login_host, org_name, services, space_name
    """
    try:
        with open(path) as f:
            config = yaml.safe_load(f.read())
        parsed = {
            "services": config['services'],
            "org_name": config['org_name'],
            "space_name": config['space_name'],
            "api_host": config['api_host'],
            "login_host": config['login_host']
        }
    except KeyError as err:
        LOGGER.info("ERROR: Required key ({0}) not in config".format(err))
        sys.exit(127)
    return parsed


def upgrade_postgres_storage(cfapi, config):
    """Upgrades postgres storage

   Configuration file should have storage related info

    """
    try:
        storage = {
            'AllocatedStorage': config['services']['postgres']['configuration_parameters']['AllocatedStorage']}
        postgres_instance_name = config['services']['postgres']['service_name']

        print(str.format('Attempting to update postgres instance with {0}', storage))
        if os.system("cf update-service {1} -c '{0}'".format(str(storage).replace("'", '"'),
                                                             postgres_instance_name)) != 0:
            print(str.format('Unable to change version of postgres instance to {0} for '
                             'service instance {1}. Exiting.', storage["AllocatedStorage"], postgres_instance_name))
            sys.exit(1)
        else:
            print(str.format('Updating postgres instance with {0}', storage))
            monitor_service_action(cfapi, [postgres_instance_name], action_type='update', wait_time=120)
    except KeyError as key_error:
        print('KeyError. Unable to change version of postgres instance', key_error)
        sys.exit(1)


def postgres_data_migration(cfapi, config):
    """Used in case of data migration

   Configuration file should have storage related info

    """
    try:
        version = {
            'EngineVersion': config['services']['postgres']['configuration_parameters']['EngineVersion']}
        postgres_instance_name = config['services']['postgres']['service_name']

        print(str.format('Attempting to update postgres instance with {0}', version))
        if os.system("cf update-service {1} -c '{0}'".format(str(version).replace("'", '"'),
                                                             postgres_instance_name)) != 0:
            print(str.format('Unable to change version of postgres instance to {0} for '
                             'service instance {1}. Exiting.', version["EngineVersion"], postgres_instance_name))
            sys.exit(1)
        else:
            print(str.format('Updating postgres instance with {0}', version))
            monitor_service_action(cfapi, [postgres_instance_name], action_type='update', wait_time=120)
    except KeyError as key_error:
        print('KeyError. Unable to change version of postgres instance', key_error)
        sys.exit(1)


