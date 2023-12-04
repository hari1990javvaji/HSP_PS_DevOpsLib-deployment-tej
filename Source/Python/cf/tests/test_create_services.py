#!/usr/bin/env python
# pylint: disable=too-many-public-methods
# pylint: disable=unused-argument
#
# All unit-test methods must be public
"""
unit test for create_services.py
"""
from __future__ import absolute_import
import unittest
import argparse
import os.path
import random
from mock import patch
import hsp_cf.create_services as cs
import six
from hsp_cf.cf import CfApi

FileError = IOError
if six.PY3:
    FileError = FileNotFoundError

app_name = 'test-app-'+str(random.randint(0, 10000))
service_name = 'test-service-'+str(random.randint(0, 10000))

def parse_args(args=None):
    """Parse command line args.

    Simple function to parse and return command line args.

    Returns:
        argparse.Namespace: An argparse.Namespace object.
    """
    parser = argparse.ArgumentParser()

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


class TestCreateServices(unittest.TestCase):
    """Parse command line args.
    Simple function to parse and return command line args.

    """

    @classmethod
    def setUpClass(self):
        """Parse command line args.
        Simple function to parse and return command line args.
        """
        my_path = os.path.abspath(os.path.dirname(__file__))
        self.config_path = os.path.join(my_path, "configurations/deployment-config.yaml")
        self.config = cs.read_config(self.config_path)
        self.config["services"]["vault-service"]["service_name"] = service_name
        args = parse_args()
        username = args.cfUsername
        password = args.cfPassword
        login_host = 'login.cloud.pcftest.com'
        api_host = 'api.cloud.pcftest.com'
        org_name = 'ENG-CICD'
        space_name = 'system_team_poc'
        self.cf_api = CfApi(username=username, password=password,
                            login_host=login_host, api_host=api_host,
                            org_name=org_name, space_name=space_name)


    def tearDown(self):
        """
        Truncate deploy.log after test cases are run
        Delete Manifest folder after TCs execution
        """
        file = open('deploy.log', 'r+')
        file.truncate(0)
        file.close()

    def test_parse_args_successful(self):
        """
        Truncate deploy.log after test cases are run
        Delete Manifest folder after TCs execution
        """
        parsed = cs.parse_args(['--config', 'test', '--cfusername',
                                "test_user", '--cfpassword', "test_password"])
        self.assertEqual(parsed.config, 'test')

    def test_parse_args_verify_cfUsername_cfPassword(self):
        """
        Truncate deploy.log after test cases are run
        Delete Manifest folder after TCs execution
        """
        parsed = cs.parse_args(['--config', 'test', '--cfusername',
                                "test_user", '--cfpassword', "test_password"])
        self.assertEqual(parsed.cfUsername, "test_user")
        self.assertEqual(parsed.cfPassword, "test_password")

    def test_read_config(self):
        """
        Truncate deploy.log after test cases are run
        Delete Manifest folder after TCs execution
        """
        config = cs.read_config(self.config_path)
        self.assertEqual(config['api_host'], "api.cloud.pcftest.com")
        self.assertEqual(config['login_host'], "login.cloud.pcftest.com")

    def test_read_config_invalid_creds(self):
        """
        Truncate deploy.log after test cases are run
        Delete Manifest folder after TCs execution
        """
        self.assertRaises(FileError, cs.read_config, "invalid_path")

    def test_create_services_managed(self):
        """
        Truncate deploy.log after test cases are run
        Delete Manifest folder after TCs execution
        """
        expected = [service_name]
        created_services = cs.create_services(self.cf_api, self.config["services"])
        print("service created : " + str(created_services))
        self.assertEqual(expected, created_services)
        response = CfApi.service_instance_guids(self.cf_api)
        CfApi.delete_service(self.cf_api, response[service_name])
        print("service deleted : " + str(created_services))

    def test_create_services_managed_invalid_broker(self):
        """
        Truncate deploy.log after test cases are run
        Delete Manifest folder after TCs execution
        """
        services = {'vault-service': {'service_name': 'vault-test-1', 'service_type': 'managed',
                                      'broker_name': 'hsdp-dummy', 'plan_name': 'vault-dummy',
                                      'optional_params': None}}
        self.assertRaises(ValueError, cs.create_services, self.cf_api, services)

    def test_create_services_managed_invalid_plan(self):
        """
        Truncate deploy.log after test cases are run
        Delete Manifest folder after TCs execution
        """
        services = {'vault-service': {'service_name': 'vault-test-1', 'service_type': 'managed',
                                      'broker_name': 'hsdp-vault', 'plan_name': 'vault-dummy',
                                      'optional_params': None}}
        self.assertRaises(ValueError, cs.create_services, self.cf_api, services)

    def test_create_services_managed_already_exists(self):
        """
        Truncate deploy.log after test cases are run
        Delete Manifest folder after TCs execution
        """
        expected = []
        print(self.config["services"])
        created_services = cs.create_services(self.cf_api, self.config["services"])
        print("service created : " + str(created_services))
        created_services = cs.create_services(self.cf_api, self.config["services"])
        print("service created : " + str(created_services))
        self.assertEqual(expected, created_services)
        response = CfApi.service_instance_guids(self.cf_api)
        CfApi.delete_service(self.cf_api, response[service_name])
        print("service deleted : " + str(created_services))

    def test_create_services_user_provided(self):
        """
        Truncate deploy.log after test cases are run
        Deletion of user provided services is not possible via API
        """
        services = {
            'vault-service': {'service_name': "user-provided", 'service_type': 'user-provided',
                              'optional_params': None,
                              'syslog_drain_url': 'http;//hsdp.test'}}
        created_services = cs.create_services(self.cf_api, services)
        print("service created : " + str(created_services))

    @patch('hsp_cf.cf.CfApi._request', return_value=app_name)
    def test_init_user_provided_services(self, mock):
        services = {'service_name': service_name, 'service_type': 'user-provided',
                              'optional_params': None,
                              'syslog_drain_url': 'http;//hsdp.test'}
        cs.init_user_provided_services(self.cf_api, services)

    def test_get_service_params(self):
        services = {'configuration_parameters': {'database_snapshot': {'use_snapshot': True}},
                     'service_name': 'user-service-test', 'service_type': 'user-provided',
                              'optional_params': None,
                              'syslog_drain_url': 'http;//hsdp.test'}
        response = cs.get_service_params(services)
        self.assertGreaterEqual(len(response),0)

    @patch('hsp_cf.create_services.check_service_status', return_value={'test':'test'})
    @patch('hsp_cf.create_services.sleep')
    def test_monitor_service_action_exit(self, mock, mock_sleep):
        """
        Truncate deploy.log after test cases are run
        Delete Manifest folder after TCs execution
        """

        self.assertRaises(SystemExit, cs.monitor_service_action,self.cf_api,
                          self.config["services"], 'create', wait_time=0)

    def test_monitor_service_action_update(self):
        """
        Truncate deploy.log after test cases are run
        Delete Manifest folder after TCs execution
        """
        response = cs.monitor_service_action(self.cf_api, self.config["services"], 'update', wait_time=120)
        self.assertTrue(response)

    def test_verify_service_names_managed(self):
        """
        Truncate deploy.log after test cases are run
        Delete Manifest folder after TCs execution
        """
        created_services = cs.create_services(self.cf_api, self.config["services"])
        print('service created')
        response = cs.verify_servicename(self.cf_api, self.config["services"], service_type='managed')
        self.assertTrue(response)
        response = CfApi.service_instance_guids(self.cf_api)
        CfApi.delete_service(self.cf_api, response[service_name])
        print("service deleted : " + str(created_services))


    def test_verify_service_names_user_provided(self):
        """
        Truncate deploy.log after test cases are run
        Delete Manifest folder after TCs execution
        """
        services = {
            'vault-service': {'service_name': 'user-service-test', 'service_type': 'user-provided',
                              'optional_params': None,
                              'syslog_drain_url': 'http;//hsdp.test'}}
        response = cs.verify_servicename(self.cf_api, services, service_type='user-provided')
        self.assertTrue(response)

    def test_verify_service_names_managed_no_service_type(self):
        """
        Truncate deploy.log after test cases are run
        Delete Manifest folder after TCs execution
        """
        self.assertRaises(SystemExit, cs.verify_servicename, self.cf_api, self.config["services"])

    @patch('hsp_cf.create_services.os.system', return_value=1)
    def test_postgres_data_migration_failure(self, os_mock):
        """
        Truncate deploy.log after test cases are run
        Delete Manifest folder after TCs execution
        """

        config = {'services': {'postgres':
                                   {'service_name': 'postgres-test-1', 'service_type':
                                       'managed', 'broker_name': 'hsdp-vault', 'plan_name':
                                        'vault-us-east-1', 'configuration_parameters':
                                        {'EngineVersion': 1.0}}}}

        self.assertRaises(SystemExit, cs.postgres_data_migration, self.cf_api, config)

    @patch('hsp_cf.create_services.os.system', return_value=0)
    @patch('hsp_cf.create_services.monitor_service_action', return_value=True)
    def test_postgres_data_migration_success(self, os_mock, monitor_mock):
        """
        Truncate deploy.log after test cases are run
        Delete Manifest folder after TCs execution
        """
        config = {'services': {'postgres':
                                   {'service_name': 'postgres-test-1', 'service_type': 'managed',
                                    'broker_name': 'hsdp-vault', 'plan_name': 'vault-us-east-1',
                                    'configuration_parameters': {'EngineVersion': 1.0}}}}
        cs.postgres_data_migration(self.cf_api, config)

    @patch('hsp_cf.create_services.os.system', return_value=1)
    def test_upgrade_postgres_storage_failure(self, os_mock):
        """
        Truncate deploy.log after test cases are run
        Delete Manifest folder after TCs execution
        """
        config = {'services': {'postgres':
                                   {'service_name': 'postgres-test-1', 'service_type': 'managed',
                                    'broker_name': 'hsdp-vault', 'plan_name': 'vault-us-east-1',
                                    'configuration_parameters': {'AllocatedStorage': '2GB'}}}}
        self.assertRaises(SystemExit, cs.upgrade_postgres_storage, self.cf_api, config)

    @patch('hsp_cf.create_services.os.system', return_value=0)
    @patch('hsp_cf.create_services.monitor_service_action', return_value=True)
    def test_upgrade_postgres_storage_success(self, os_mock, monitor_mock):
        """
        Truncate deploy.log after test cases are run
        Delete Manifest folder after TCs execution
        """
        config = {'services': {'postgres':
                                   {'service_name': 'postgres-test-1', 'service_type': 'managed',
                                    'broker_name': 'hsdp-vault', 'plan_name': 'vault-us-east-1',
                                    'configuration_parameters': {'AllocatedStorage': '2GB'}}}}
        cs.upgrade_postgres_storage(self.cf_api, config)


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    itersuite = unittest.TestLoader().loadTestsFromTestCase(TestCreateServices)
    runner.run(itersuite)
