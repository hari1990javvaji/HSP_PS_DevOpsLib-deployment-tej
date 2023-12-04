"""Test Vault service creds for storing/reading files from vault"""
import argparse
import unittest
import os
from mock import patch
import hsp_vault.VaultOperations as VaultOperations


def parse_args(args=None):
    """Parse command line args.
    Returns:
        argparse.Namespace: An argparse.Namespace object
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-s',
                        '--secret_id',
                        dest='secret_id',
                        default=None,
                        required=False,
                        help='secret_id')

    return parser.parse_args( args )
    

class TestVaultOperations(unittest.TestCase):
    """Unit test cases for vault operations"""
    def setUp(self):
        args = parse_args()
        self.secret_id = args.secret_id

        root_dir = os.path.abspath(os.path.dirname(__file__))

        self.key = {
            "endpoint": "https://vproxy.us-east.philips-healthsuite.com/",
            "role_id": "5f6d5c0e-b752-524e-35b1-197ff9fced90",
            "service_secret_path": "/v1/cf/d74b4ac3-deaf-4c5d-ab8c-c50ac72c44f4/secret"
        }

        self.client = VaultOperations.vault_client_create(self.key['endpoint'],
                                                          self.key['role_id'],
                                                          self.secret_id)
        self.directory = os.path.join(root_dir, 'test-data')

    def test_vault_client_create_success(self):
        """Testcase to create vault client with invalid url"""
        create_vault = VaultOperations.vault_client_create(self.key['endpoint'],
                                                           self.key['role_id'],
                                                           self.secret_id)
        self.assertIsNotNone(create_vault)

    @patch('hsp_vault.VaultOperations.print')
    def test_vault_client_create_invalid(self, mock_print):
        """Testcase to create vault client with invalid url """
        endpoint = "http://proxy.us-east.philips-health"
        create_vault = VaultOperations.vault_client_create(endpoint,
                                                           self.key['role_id'],
                                                           self.secret_id)
        self.assertRaises(Exception, create_vault)

    @patch('hsp_vault.VaultOperations.print')
    def test_vault_client_create_exception(self, mock_print):
        """Testcase if it throws exception while creating vault client"""
        self.assertRaises(TypeError, VaultOperations.vault_client_create)

    def test_store_value_success(self):
        """Testcase for storing file content"""
        remote_path = self.key['service_secret_path'].strip('v1/') + '/' + "new1"
        input_value = (open(os.path.join(self.directory, 'new1.txt')).read())
        store = VaultOperations.store_value(self.client, remote_path, {"file_contents": input_value})
        self.assertEqual(store, True)

    @patch('hsp_vault.VaultOperations.print')
    def test_store_value_invalid(self, mock_print):
        """Testcase for storing invalid file content"""
        remote_path = "/v1/cf/dba80dgksjfdsbdjydtwndsd".strip('v1/') + '/' + "new2"
        value = open(os.path.join(self.directory, 'new5.txt')).read()
        store = VaultOperations.store_value(self.client, remote_path, value)
        self.assertNotEqual(store, True)

    def test_read_value_success(self):
        """Testcase for reading file content"""
        remote_path = self.key['service_secret_path'].strip('v1/') + '/' + "new1"
        input_value = (open(os.path.join(self.directory, 'new1.txt')).read())
        VaultOperations.store_value(self.client, remote_path, {"value": input_value})
        store = VaultOperations.read_value(self.client, remote_path)
        self.assertNotEqual(store, False)

    @patch('hsp_vault.VaultOperations.print')
    def test_read_value_exception(self, mock_print):
        """Testcase to read file content if it throws exception"""
        self.assertRaises(TypeError, VaultOperations.read_value)

    def test_delete_value_success(self):
        """Testcase for deleting file content"""
        remote_path = self.key['service_secret_path'].strip('v1/') + '/' + "new2"
        deleting_value = VaultOperations.delete_value(self.client, remote_path)
        self.assertEqual(deleting_value, True)

    @patch('hsp_vault.VaultOperations.print')
    def test_delete_value_exception(self, mock_print):
        """Testcase to delete file content if it throws exception"""
        self.assertRaises(TypeError, VaultOperations.delete_value)

    def test_read_secret_success(self):
        """testcase to read vault secret"""
        vaultfile = self.key['service_secret_path'].strip('v1/') + '/' + "new1"
        read_secret = VaultOperations.read_secret(self.client, vaultfile)
        self.assertNotEqual(read_secret, False)

    @patch('hsp_vault.VaultOperations.print')
    def test_read_secret_invalid(self, mock_print):
        """testcase for invalid vault secrets"""
        self.assertRaises(Exception, VaultOperations.read_secret)

    def test_store_config_file_plain_text(self):
        """testcase for storing plain text config file"""
        remote_path = self.key['service_secret_path'].strip('v1/') + '/' + "new1"
        vaultfile = os.path.join(self.directory, 'new1.txt')
        store_content = "plain_text"
        store_config = VaultOperations.store_config_file(self.client, remote_path,
                                                         vaultfile, store_content)
        self.assertEqual(store_config, True)

    def test_store_config_file_encoded(self):
        """testcase for storing encoded config file"""
        remote_path = self.key['service_secret_path'].strip('v1/') + '/' + "new1"
        vaultfile = os.path.join(self.directory, 'new1.txt')
        store_encoded_content = True
        store_config = VaultOperations.store_config_file(self.client, remote_path,
                                                         vaultfile, store_encoded_content)
        self.assertEqual(store_config, True)

    @patch('hsp_vault.VaultOperations.print')
    def test_store_config_file_exception(self, mock_print):
        """testcase for storing config file with invalid vault_path"""
        remote_path = self.key['service_secret_path'].strip('v1/') + '/' + "new17"
        vaultfile = os.path.join(self.directory, 'new8.txt')
        store_config = VaultOperations.store_config_file(self.client, remote_path, vaultfile)
        self.assertRaises(Exception, store_config)

    def test_read_config_file(self):
        """Testcase to read config plain text file"""
        vault_remote_path = self.key['service_secret_path'].strip('v1/') + '/' + "new1"
        vaultfile = os.path.join(self.directory, 'new1.txt')
        store_encoded_content = "plain_text"
        VaultOperations.store_config_file(self.client, vault_remote_path, vaultfile,
                                          store_encoded_content)
        read_decoded_content = "plain_text"
        readfile = VaultOperations.read_config_file(self.client, vault_remote_path,
                                                    read_decoded_content)
        self.assertNotEqual(readfile, False)

    def test_read_config_file_decoded(self):
        """Testcase to read encoded config file"""
        vault_remote_path = self.key['service_secret_path'].strip('v1/') + '/' + "new1"
        vaultfile = os.path.join(self.directory, 'new1.txt')
        store_encoded_content = True
        VaultOperations.store_config_file(self.client, vault_remote_path,
                                          vaultfile, store_encoded_content)
        read_encoded_content = True
        readfile = VaultOperations.read_config_file(self.client, vault_remote_path,
                                                    read_encoded_content)
        self.assertNotEqual(readfile, False)

    def test_read_config_file_binary(self):
        """Testcase to read binary file"""
        vault_remote_path = self.key['service_secret_path'].strip('v1/') + '/' + "sample_bin"
        vaultfile = os.path.join(self.directory, 'sample.bin')
        store_encoded_content = "plain_binary"
        VaultOperations.store_binary_config_file(self.client, vault_remote_path,
                                                 vaultfile, store_encoded_content)
        read_encoded_content = "plain_binary"
        readfile = VaultOperations.read_config_file(self.client, vault_remote_path,
                                                    read_encoded_content)
        self.assertNotEqual(readfile, False)

    def test_read_config_file_encoded_binary(self):
        """Testcase to read binary encoded file"""
        vault_remote_path = self.key['service_secret_path'].strip('v1/') + '/' + "sample_bin"
        vaultfile = os.path.join(self.directory, 'sample.bin')
        store_encoded_content = True
        VaultOperations.store_binary_config_file(self.client, vault_remote_path,
                                                 vaultfile, store_encoded_content)
        read_encoded_content = True
        readfile = VaultOperations.read_config_file(self.client, vault_remote_path,
                                                    read_encoded_content)
        self.assertNotEqual(readfile, False)

    @patch('hsp_vault.VaultOperations.print')
    def test_read_config_invalid_file(self, mock_print):
        """Testcase to read config file"""
        vault_remote_path = self.key['service_secret_path'].strip('v1/') + '/' + "sample"
        readfile = VaultOperations.read_config_file(self.client, vault_remote_path)

        self.assertRaises(Exception, readfile)

    def test_store_binary_config_file(self):
        """Testcase for storing plain binary file"""
        remote_path = self.key['service_secret_path'].strip('v1/') + '/' + "sample_bin"
        vaultfile = os.path.join(self.directory, 'sample.bin')
        store_encoded_content = "plain_binary"
        storing_binary = VaultOperations.store_binary_config_file(self.client,
                                                                  remote_path,
                                                                  vaultfile,
                                                                  store_encoded_content)
        self.assertEqual(storing_binary, True)

    def test_store_binary_config_file_encoded(self):
        """Testcase for storing encoded binary file"""
        remote_path = self.key['service_secret_path'].strip('v1/') + '/' + "sample_bin"
        vaultfile = os.path.join(self.directory, 'sample.bin')
        store_encoded_content = True
        storing_binary = VaultOperations.store_binary_config_file(self.client,
                                                                  remote_path,
                                                                  vaultfile,
                                                                  store_encoded_content)
        self.assertEqual(storing_binary, True)

    @patch( 'hsp_vault.VaultOperations.print' )
    def test_store_binary_config_file_invalid(self, mock_print):
        """Testcase for storing invalid binary file"""
        remote_path1 = self.key['service_secret_path'].strip('v1/') + '/' + "sample5"
        vaultfile = os.path.join(self.directory, 'sample.html')
        storing_binary = VaultOperations.store_binary_config_file(self.client, remote_path1,
                                                                  vaultfile)
        self.assertRaises(Exception, storing_binary)

    def test_store_json_file_success(self):
        """Testcase for storing json file"""
        remote_path = self.key['service_secret_path'].strip('v1/') + '/' + "new1"
        vaultfile = os.path.join(self.directory, 'file1.json')
        storing_json = VaultOperations.store_json_file(self.client, remote_path, vaultfile)
        self.assertEqual(storing_json, True)

    @patch('hsp_vault.VaultOperations.print')
    def test_store_json_file_invalid(self, mock_print):
        """Testcase for storing invalid file throws exception"""
        remote_path = self.key['service_secret_path'].strip('v1/') + '/' + "new1"
        vaultfile = os.path.join(self.directory, 'new1.txt')
        storing_json = VaultOperations.store_json_file(self.client, remote_path, vaultfile)
        self.assertRaises(Exception, storing_json)

    def test_read_json_file(self):
        """Testcase for reading json file"""
        vault_remote_path = self.key['service_secret_path'].strip('v1/') + '/' + "new1"
        vaultfile = os.path.join(self.directory, 'file1.json')
        VaultOperations.store_json_file(self.client, vault_remote_path, vaultfile)
        read_json = VaultOperations.read_json_file(self.client, vault_remote_path)
        self.assertNotEqual(read_json, False)

    @patch('hsp_vault.VaultOperations.print')
    def test_read_json_file_exception(self, mock_print):
        """Testcase for reading json file with invalid remote_path"""
        vault_remote_path = "/v1/cf/dba80c94".strip('v1/') + '/' + "new1"
        read_json = VaultOperations.read_json_file(self.client, vault_remote_path)
        self.assertRaises(Exception, read_json)


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    itersuite = unittest.TestLoader().loadTestsFromTestCase(TestVaultOperations)
    runner.run(itersuite)
