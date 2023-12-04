#!/usr/bin/env python
# pylint: disable=protected-access
# pylint: disable=too-many-public-methods
# pylint: disable=unused-argument
# The protected-access warnings are disabled because the decorator
# function uses protected members of the CfApi class outside the class.
# When this is the case it is acceptable to disable these warnings.
#
# All unit-test methods must be public
# Mocked instance must be passed as an agrument but, it's not used
"""
unit test for cf.py
"""
from __future__ import absolute_import

import unittest
from collections import OrderedDict
import argparse
import random
import os.path
from six.moves import urllib
import six
from mock import patch
from hsp_cf.cf import CfApi

app_name = 'test-app-' + str(random.randint(0, 10000))
service_name = 'test-service' + str(random.randint(0, 10000))
task_name = 'test-service' + str(random.randint(0, 10000))


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


class TestCf(unittest.TestCase):
    """
    unit test class for cf.py
    """

    @classmethod
    def setUpClass(self):
        """Parse command line args.

        Simple function to parse and return command line args.

        Returns:
            argparse.Namespace: An argparse.Namespace object.

        """
        print('using:' + app_name)
        self.dummy_guid = '6d8e90f2-3fce-41ba-9d73-a1c061ed03c0'
        args = parse_args()
        username = args.cfUsername
        password = args.cfPassword
        login_host = 'login.cloud.pcftest.com'
        api_host = 'api.cloud.pcftest.com'
        org_name = 'ENG-CICD'
        space_name = 'system_team_poc'
        self.cf_api = CfApi(username=username, password=password, login_host=login_host, api_host=api_host,
                            org_name=org_name, space_name=space_name)

        my_path = os.path.abspath(os.path.dirname(__file__))
        self.config = os.path.join(my_path, "configurations/deployment-config.yaml")

    def tearDown(self):
        """
        Truncate deploy.log after test cases are run
        Delete Manifest folder after TCs execution
        """
        file = open('deploy.log', 'r+')
        file.truncate(0)
        file.close()

    def test_json_dump(self):
        """
        Truncate deploy.log after test cases are run
        Delete Manifest folder after TCs execution
        """
        data = OrderedDict({
            "name": "John",
            "age": 30,
            "city": "New York"
        })
        if six.PY2:
            json_data_expected = '{\n    "age": 30, \n    "city": "New York", \n    "name": "John"\n}'
        else:
            json_data_expected = '{\n    "age": 30,\n    "city": "New York",\n    "name": "John"\n}'
        json_data_actual = CfApi._json(data)
        self.assertEqual(json_data_expected, json_data_actual)

    def test_delete_invalid_app_raise_exp(self):
        """
        When an invalid app or if the app is not present and it's being deleted, 404 error is expected
        """
        self.assertRaises(urllib.error.HTTPError, CfApi.delete_app, self.cf_api, self.dummy_guid)

    def test_services(self):
        """
        return the list of services along with metadata
        """
        response = CfApi.services(self.cf_api)
        self.assertGreaterEqual(len(response), 0)

    def test_services_guids(self):
        """
        return the list of services along with metadata
        """
        service_guids = CfApi.service_guids(self.cf_api)
        self.assertGreaterEqual(len(service_guids), 0)

    def test_services_plans(self):
        """
        return the list of services along with metadata
        """
        service_plans = CfApi.service_plans(self.cf_api)
        self.assertGreaterEqual(len(service_plans), 0)

    def test_services_plans_guids(self):
        """
        return the list of services along with metadata
        """
        service_guids = CfApi.service_guids(self.cf_api)
        service_plans = CfApi.service_plan_guids(self.cf_api, service_guids['hsdp-rds'])
        self.assertGreaterEqual(len(service_plans), 0)

    def test_services_plans_guids_invalid_service_guid(self):
        """
        return the list of services along with metadata
        """
        response = CfApi.service_plan_guids(self.cf_api, "213")
        self.assertGreaterEqual(len(response), 0)

    def test_services_instances(self):
        """
        return the list of services along with metadata
        """
        response = CfApi.service_instances(self.cf_api)
        self.assertGreaterEqual(len(response), 0)

    def test_services_keys(self):
        """
        return the list of services along with metadata
        """
        response = CfApi.service_keys(self.cf_api)
        self.assertGreaterEqual(len(response), 0)


    def test_create_services_delete_services(self):
        """
        return the list of services along with metadata
        """
        CfApi.create_service(self.cf_api, service_name, 'hsdp-vault', 'vault-us-east-1')
        response = CfApi.service_instance_guids(self.cf_api)
        CfApi.delete_service(self.cf_api, response[service_name])

    def test_create_services_delete_services_no_service(self):
        """
        return the list of services along with metadata
        """
        self.assertRaises(urllib.error.HTTPError, CfApi.delete_service, self.cf_api, "dummy-service")

    @patch('hsp_cf.cf.CfApi._request', return_value=app_name)
    def test_create_user_provided_service(self, mock_request):
        """
        return the list of services along with metadata
        """
        response = CfApi.create_user_provided_service(self.cf_api, service_name, {"creds": "dummy"}, 'log-drain')
        self.assertEqual(response, app_name)

    def test_user_provided_service_instances(self):
        """
               return the list of services along with metadata
               """
        response = CfApi.user_provided_service_instances(self.cf_api)
        self.assertIsNotNone(response)

    @patch('hsp_cf.cf.CfApi._request', return_value=service_name)
    def test_create_service_keys(self, mock):
        """
        return the list of services along with metadata
        """
        response = CfApi.create_service_keys(self.cf_api, self.dummy_guid, service_name)
        self.assertIsNotNone(response)

    def test_apps(self):
        """
        return the list of services along with metadata
        """
        response = CfApi.apps(self.cf_api)
        self.assertGreaterEqual(len(response), 0)

    @patch('hsp_cf.cf.CfApi._request', return_value=app_name)
    def test_create_app(self, mock):
        """
        Truncate deploy.log after test cases are run
        Delete Manifest folder after TCs execution
        """
        response = CfApi.create_app(self.cf_api, app_name)
        print('mock-app created.' + str(response))

    def test_create_delete_app_no_app(self):
        """
        Truncate deploy.log after test cases are run
        Delete Manifest folder after TCs execution
        """
        self.assertRaises(urllib.error.HTTPError, CfApi.delete_app, self.cf_api, "dummy-app")

    apps = [{u'entity': {u'name': u'test-app-592'},
             u'metadata': {u'guid': u'd19cca7d-1e32-4a06-85d2-add57ea20d45'}}]

    @patch('hsp_cf.cf.CfApi.apps', return_value=apps)
    def test_app_guid(self, mock):
        """
        return the list of services along with metadata
        """
        response = CfApi.app_guids(self.cf_api)
        self.assertGreaterEqual(len(response), 0)

    @patch('hsp_cf.cf.CfApi.apps', return_value=apps)
    def test_app_guid_app_name(self, mock):
        """
        return the list of services along with metadata
        """
        response = CfApi.app_guids(self.cf_api, app_name)
        self.assertGreaterEqual(len(response), 0)

    def test_service_instance_guids(self):
        """
        return the list of services along with metadata
        """
        service_instance_guids = CfApi.service_instance_guids(self.cf_api)
        self.assertGreaterEqual(len(service_instance_guids), 0)

    def test_service_instance_guids_filter(self):
        """
        return the list of services along with metadata
        """
        CfApi.create_service(self.cf_api, service_name, 'hsdp-vault', 'vault-us-east-1')
        service_instance_guids = CfApi.service_instance_guids(self.cf_api, service_name)
        self.assertGreaterEqual(len(service_instance_guids), 0)
        response = CfApi.service_instance_guids(self.cf_api)
        CfApi.delete_service(self.cf_api, response[service_name])

    @patch('hsp_cf.cf.CfApi._request', return_value='service bind')
    def test_bind_services(self, mock):
        """
        return the list of services along with metadata
        """
        response = CfApi.bind_service(self.cf_api, self.dummy_guid,
                                      self.dummy_guid)
        self.assertEqual(response, 'service bind')

    @patch('hsp_cf.cf.CfApi._request', return_value='service unbind')
    def test_unbind_services(self, mock):
        """
        return the list of services along with metadata
        """
        response = CfApi.unbind_service(self.cf_api, self.dummy_guid)
        self.assertEqual(response, 'service unbind')

    def test_unbind_services_invalid_service(self):
        """
        return the list of services along with metadata
        """
        CfApi.service_instance_guids(self.cf_api)
        CfApi.app_guids(self.cf_api)
        self.assertRaises(urllib.error.HTTPError, CfApi.unbind_service, self.cf_api,
                          self.dummy_guid)

    @patch('hsp_cf.cf.CfApi._request', return_value='task created')
    def test_create_task(self, mock):
        """
        return the list of services along with metadata
        """
        response = CfApi.create_task(self.cf_api, 'start', task_name,
                                     '3242354')
        self.assertEqual('task created', response)

    def test_create_task_invalid_app_guid(self):
        """
        return the list of services along with metadata
        """
        self.assertRaises(urllib.error.HTTPError, CfApi.create_task, self.cf_api, 'start', task_name, self.dummy_guid)

    @patch('hsp_cf.cf.CfApi._request', return_value='all tasks')
    def test_get_task(self, mock):
        """
        return the list of services along with metadata
        """
        response = CfApi.get_task(self.cf_api, self.dummy_guid)
        self.assertGreaterEqual(len(response), 0)

    def test_get_task_invalid_app_guid(self):
        """
        return the list of services along with metadata
        """
        self.assertRaises(urllib.error.HTTPError, CfApi.get_task, self.cf_api, self.dummy_guid)

    def test_list_task(self):
        """
        return the list of services along with metadata
        """
        response = CfApi.list_task(self.cf_api)
        self.assertGreaterEqual(len(response), 0)

    def test_resolve_instance_guids(self):
        """
        return the list of services along with metadata
        """
        CfApi._resolve_instance_guids(self.cf_api)

    def test_refresh_token(self):
        """
        return the list of services along with metadata
        """
        CfApi.refresh_token(self.cf_api)


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    itersuite = unittest.TestLoader().loadTestsFromTestCase(TestCf)
    runner.run(itersuite)
