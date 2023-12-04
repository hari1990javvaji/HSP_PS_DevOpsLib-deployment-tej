"""Test Vault Operations for storing/reading files from vault"""
import argparse
import unittest
from cloudfoundry_client.client import CloudFoundryClient
import hsp_vault.VaultServiceCreds as VaultServiceCreds
import os
from mock import patch


def parse_args(args=None):
    """Parse command line args.
    Returns:
        argparse.Namespace: An argparse.Namespace object
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-u',
                        '--cf_user_name',
                        dest='cf_user_name',
                        default=None,
                        required=False,
                        help='Username of the ldap to authenticate...')
    parser.add_argument('-p',
                        '--cf_password',
                        dest='cf_password',
                        default=None,
                        required=False,
                        help='Password of the ldap to authenticate...')

    return parser.parse_args(args)


class TestVaultServiceCreds(unittest.TestCase):
    """Class for unit testing TestVaultServiceCreds"""
    def setUp(self):
        args = parse_args()
        self.username = args.cf_user_name
        self.password = args.cf_password

        self.key = {
            "cf_url": "https://api.cloud.pcftest.com",
            "cf_org": "ENG-CICD",
            "cf_space": "DevOpsLib",
            "vault_service_name": "vault_system_team_1"
        }

        self.proxy = dict(http=os.environ.get('http_proxy'), https=os.environ.get('https_proxy'))
        self.client = CloudFoundryClient(self.key['cf_url'], proxy=self.proxy,
                                         skip_verification=True)
        self.client.init_with_user_credentials(login=self.username, password=self.password)

    def test_get_space_guid(self):
        """Testcase to get space_guid"""
        response = VaultServiceCreds.get_space_guid(self.client, self.key['cf_org'],
                                                    self.key['cf_space'])
        self.assertIsNotNone(response)

    @patch('hsp_vault.VaultServiceCreds.print')
    def test_get_space_guid_invalid_org(self, mock_print):
        """Testcase to get space_guid for invalid cf_org """
        response = VaultServiceCreds.get_space_guid(self.client, "", self.key['cf_space'])
        self.assertIsNone(response)

    @patch('hsp_vault.VaultServiceCreds.print')
    def test_get_space_guid_invalid_space(self, mock_print):
        """Testcase to get space_guid for invalid cf_space """
        response = VaultServiceCreds.get_space_guid(self.client, self.key['cf_org'], None)
        self.assertIsNone(response)

    def test_get_service_guid(self):
        """Testcase to get service_guid"""
        space_guid = VaultServiceCreds.get_space_guid(self.client,
                                                      self.key['cf_org'],
                                                      self.key['cf_space'])
        response = VaultServiceCreds.get_service_guid(self.client,
                                                      space_guid,
                                                      self.key['vault_service_name'])
        self.assertIsNotNone(response)

    @patch('hsp_vault.VaultServiceCreds.print')
    def test_get_service_guid_invalid_space_guid(self, mock_print):
        """Testcase to get service_guid with invalid space_guid"""
        space_guid = ""
        response = VaultServiceCreds.get_service_guid(self.client, space_guid,
                                                      self.key['vault_service_name'])
        self.assertIsNone(response)

    @patch('hsp_vault.VaultServiceCreds.print')
    def test_get_service_guid_invalid_service_name(self, mock_print):
        """Testcase to get service_guid with invalid vault service name"""
        space_guid = VaultServiceCreds.get_space_guid(self.client, self.key['cf_org'],
                                                      self.key['cf_space'])
        self.assertIsNone(VaultServiceCreds.get_service_guid(self.client, space_guid, ""))

    def test_get_service_key_creds(self):
        """Testcase to get service_key_creds"""
        space_guid = VaultServiceCreds.get_space_guid(self.client, self.key['cf_org'],
                                                      self.key['cf_space'])
        service_guid = VaultServiceCreds.get_service_guid(self.client, space_guid,
                                                          self.key['vault_service_name'])
        service_key_creds = VaultServiceCreds.get_service_key_creds(self.client, service_guid)
        self.assertIsNotNone(service_key_creds)

    @patch('hsp_vault.VaultServiceCreds.print')
    def test_get_service_key_creds_invalid_space_guid(self, mock_print):
        """Testcase to get service_key_creds with invalid space guid"""
        service_guid = VaultServiceCreds.get_service_guid(self.client, None,
                                                          self.key['vault_service_name'])
        self.assertIsNotNone(VaultServiceCreds.get_service_key_creds(self.client, service_guid))

    @patch('hsp_vault.VaultServiceCreds.print')
    def test_get_service_key_creds_invalid_service_name(self, mock_print):
        """Testcase to get service_key_creds with invalid service name"""
        space_guid = VaultServiceCreds.get_space_guid(self.client, self.key['cf_org'], self.key['cf_space'])
        service_guid = VaultServiceCreds.get_service_guid(self.client, space_guid, None)
        self.assertIsNone(VaultServiceCreds.get_service_key_creds(self.client, service_guid))

    def test_get_vault_service_credentials(self):
        """Testcase to get vault service credentials through commandline"""
        command_type = None
        vault_service_cred = VaultServiceCreds.get_vault_service_credentials(self.key['cf_url'],
                                                                             self.username,
                                                                             self.password,
                                                                             self.key['cf_org'],
                                                                             self.key['cf_space'],
                                                                             self.key['vault_service_name'],
                                                                             command_type)
        self.assertIsNotNone(vault_service_cred)

    @patch('hsp_vault.VaultServiceCreds.print')
    def test_get_vault_service_credentials_invalid(self, mock_print):
        """Testcase to get vault service credentials through commandline with invalid service"""
        command_type = None
        vault_service_cred = VaultServiceCreds.get_vault_service_credentials(self.key['cf_url'],
                                                                             self.username,
                                                                             self.password,
                                                                             self.key['cf_org'],
                                                                             self.key['cf_space'],
                                                                             "",
                                                                             command_type)
        self.assertRaises(Exception, vault_service_cred)

    def test_get_vault_service_credentials_cf_client_api(self):
        """Testcase to get vault service credentials through cf_client API"""
        command_type = "cf_client"
        cf_vault_creds = VaultServiceCreds.get_vault_service_credentials(self.key['cf_url'],
                                                                         self.username,
                                                                         self.password,
                                                                         self.key['cf_org'],
                                                                         self.key['cf_space'],
                                                                         self.key['vault_service_name'],
                                                                         command_type)
        self.assertIsNotNone(cf_vault_creds)

    @patch('hsp_vault.VaultServiceCreds.print')
    def test_get_vault_service_credentials_cf_client_invalid_service(self, mock_print):
        """Testcase to get vault service credentials through cf_client with invalid service guid"""
        command_type = "cf_client"
        service_guid = VaultServiceCreds.get_service_guid(self.client, "",
                                                          self.key['vault_service_name'])
        VaultServiceCreds.get_service_key_creds(self.client, service_guid)
        cf_vault_creds = VaultServiceCreds.get_vault_service_credentials(self.key['cf_url'],
                                                                         self.username,
                                                                         self.password,
                                                                         self.key['cf_org'],
                                                                         self.key['cf_space'],
                                                                         self.key['vault_service_name'],
                                                                         command_type)
        self.assertRaises(Exception, cf_vault_creds)

    def test_cf_cli_get_key(self):
        """Testcase to get cf cli service credentials"""
        get_key = VaultServiceCreds.cf_cli_get_key(self.key['cf_url'],
                                                   self.username,
                                                   self.password,
                                                   self.key['cf_org'],
                                                   self.key['cf_space'],
                                                   self.key['vault_service_name'])
        self.assertIsNotNone(get_key)

    def test_cf_get_key(self):
        """Testcase to get cf cli service credentials"""
        get_key = VaultServiceCreds.cf_get_key(self.key['cf_url'],
                                               self.username,
                                               self.password,
                                               self.key['cf_org'],
                                               self.key['cf_space'],
                                               self.key['vault_service_name'])
        self.assertIsNotNone(get_key)

    @patch('hsp_vault.VaultServiceCreds.print')
    def test_cf_get_key_invalid_space(self, mock_print):
        """Testcase to get cf cli service credentials"""
        get_key = VaultServiceCreds.cf_get_key(self.key['cf_url'],
                                               self.username,
                                               self.password,
                                               self.key['cf_org'],
                                               "",
                                               self.key['vault_service_name'])
        self.assertIsNone(get_key)

    def test_execute_command(self):
        """Testcase for executing command"""
        command = ["cf", "login", "-a", self.key['cf_url'],
                   "-u", self.username,
                   "-p", self.password,
                   "-o", self.key['cf_org'],
                   "-s", self.key['cf_space']]
        execute = VaultServiceCreds.execute_command(command)
        self.assertIsNotNone(execute)

    @patch('hsp_vault.VaultServiceCreds.print')
    def test_execute_command_invalid(self, mock_print):
        """Testcase for executing command with invalid url"""
        command = ["cf", "login", "-a", "https://www.python.org/",
                   "-u", self.username,
                   "-p", self.password,
                   "-o", self.key['cf_org'],
                   "-s", self.key['cf_space']]
        execute = VaultServiceCreds.execute_command(command)
        self.assertRaises(Exception, execute)

    def test_cf_cli_login(self):
        """Testcase for command line login"""
        cli_login = VaultServiceCreds.cf_cli_login(self.key['cf_url'],
                                                   self.username,
                                                   self.password,
                                                   self.key['cf_org'],
                                                   self.key['cf_space'])

        self.assertIsNotNone(cli_login)

    @patch('hsp_vault.VaultServiceCreds.print')
    def test_cf_cli_login_invalid_url(self, mock_print):
        """Testcase for command line with invalid url throws exception"""
        cli_login = VaultServiceCreds.cf_cli_login("https://www.python.org/",
                                                   self.username,
                                                   self.password,
                                                   self.key['cf_org'],
                                                   self.key['cf_space'])

        self.assertRaises(Exception, cli_login)

    @patch('hsp_vault.VaultServiceCreds.print')
    def test_cf_cli_login_invalid_cf_space(self, mock_print):
        """Testcase for command line with invalid cf_space throws exception"""
        cli_login = VaultServiceCreds.cf_cli_login(self.key['cf_url'],
                                                   self.username,
                                                   self.password,
                                                   self.key['cf_org'],
                                                   "")
        self.assertRaises(Exception, cli_login)

    @patch('hsp_vault.VaultServiceCreds.print')
    def test_create_service_key_invalid_key(self, mock_print):
        """Testcase to create service key"""
        service_key = ""
        response = VaultServiceCreds.create_service_key(self.key['vault_service_name'],
                                                        service_key)
        self.assertFalse(response)

    @patch('hsp_vault.VaultServiceCreds.print')
    def test_get_service_key_credentials_invalid(self, mock_print):
        """Testcase to get service key credentials"""
        service_key = ""
        get_key = VaultServiceCreds.get_service_key_credentials(self.key['vault_service_name'],
                                                                service_key)
        self.assertIsNone(get_key)

    def test_is_service_exists(self):
        """Testcase to check if service exist or not"""
        service_exist = VaultServiceCreds.is_service_exists(self.key['vault_service_name'])
        self.assertEqual(service_exist, True)

    @patch('hsp_vault.VaultServiceCreds.print')
    def test_is_service_exists_fails(self, mock_print):
        """Testcase to check if service exist or not"""
        service_exist = VaultServiceCreds.is_service_exists("")
        self.assertFalse(service_exist)

    def test_exit_if_error(self):
        """Test case to check if exit error"""
        self.output = 'OK'
        self.assertIsNone(VaultServiceCreds.exit_if_error(self.output))


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    itersuite = unittest.TestLoader().loadTestsFromTestCase(TestVaultServiceCreds)
    runner.run(itersuite)
