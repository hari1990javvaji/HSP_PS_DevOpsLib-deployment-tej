#! /usr/bin/python
# Base64 for encoding and decoding
# Hvac is Hashicorp Vault implementation for creating vault Client without storing in filesystem

"""Vault Operations script"""
import base64
import json
import hvac


def vault_client_create(vault_proxy_url, role_id, secret_id):
    """vault_client_create():Method to Create Vault Client using HVAC
    :param vault_proxy_url:Vault Proxy URL
    :param role_id: RoleID of Vault
    :param secret_id: SecretID of Vault
    :return:vault_client
    Usage: vault_client=VaultOperations.vault_client_create('https://vproxy.cloud.pcftest.com',
            '<RoleID>','<SecretID')
    Note:1)Do not console log or share the RoleID, SecretID inside/outside
        2)Vault Token is not stored in FileSystem, it is in Object(better secure)
    """
    try:
        vault_client = hvac.Client(url=vault_proxy_url)
        client_token = vault_client.auth_approle(role_id=role_id, secret_id=secret_id)
        vault_client.token = client_token['auth']['client_token']
        return vault_client
    except Exception as e:
        print('Creating Vault Client is failed')
        print(e)


def store_value(vault_client, vault_path, input_value):
    """store_value: Write single value functions
    :param vault_client:Vault client
    :param vault_path:vault_client path
    :param input_value: data to be stored in vault
    :return:None
    """
    try:
        vault_client.write(vault_path, **input_value)
        return True

    except Exception as e:
        print("Failed to store value")
        print(e)


def read_value(vault_client, vault_path):
    """read_value: read the single value functions
    :param vault_client:Vault client
    :param vault_path:vault_client path
    :return: val
    """
    try:
        downloaded_value = vault_client.read(vault_path)['data']['value']
        decoded_data = base64.b64decode(downloaded_value)
    except TypeError:
        return None
    return decoded_data


def delete_value(vault_client, vault_path):
    """delete_value: deleting the single value functions
    :param vault_client:Vault client
    :param vault_path:vault_client path
    :return:
    """
    try:
        vault_client.delete(vault_path)
    except TypeError:
        print("TypeError: Type Mismatch")
        return False
    return True


def read_secret(vault_client, vault_path):
    """ read_secret: Method to Read Credentials. Note1: Use vault path /secret/cred
    :param vault_client: HVAC client for Vault
    :param vault_path: Path for Vault
    :return: None
   """
    try:
        return vault_client.read(vault_path)['data']
    except Exception as e:
        print("Vault path doesn't exist")
        print(e)


def store_config_file(vault_client, vault_path, file_path, store_encoded_content=None):
    """ store_config_file: Method to store any pub file/ Config file content to Vault.
    :param vault_client: HVAC client for Vault
    :param vault_path: Path for Vault
    :param file_path: complete path of the file from local workspace
    :return:None
    Encoding: Uses Base64 encode to write Config file to Vault
    """
    try:
        if store_encoded_content != True:
            with open(file_path, "r") as f:
                file_object = f.read()
                vault_client.write(vault_path, file=file_object)
                return True
        else:
            with open(file_path, "r") as f:
                file_object = f.read()
                vault_client.write(vault_path, file=file_object)
                file_obj_encode = file_object.encode('ascii')
                encoded_data = base64.b64encode(file_obj_encode)
                encoded_data_decode_string = encoded_data.decode('ascii')
                vault_client.write(vault_path, file=encoded_data_decode_string)
                return True
    except Exception as e:
        print("Failed to store config file content to Vault")
        print(e)
        return False


def store_binary_config_file(vault_client, vault_path, file_path, store_encoded_content=None):
    """ store_binary_config_file(): Method to write Config file to Vault.
    :param vault_client: HVAC client for Vault
    :param vault_path: Path for Vault
    :param file_path: complete path of the file from local workspace
    :return:
    """
    try:
        if store_encoded_content != True:
            with open(file_path, "rb") as f:
                file_object = f.read()
                bytes_to_string = file_object.decode( 'utf-8' )
                vault_client.write(vault_path, file=bytes_to_string)
                return True
        else:
            with open(file_path, "rb") as f:
                encoded_data = base64.b64encode(f.read())
                base64_string = encoded_data.decode('utf-8')
                vault_client.write(vault_path, file=base64_string)
                return True

    except Exception as e:
        print("Failed to store binary file")
        print(e)
        return False


def read_config_file(vault_client, vault_path, read_decoded_content=None):
    """ read_config_file(): Method to read Pub file/config file content from Vault.
    :param vault_client: HVAC client for Vault
    :param vault_path: Path for Vault
    :return: File content
    Decoding: Uses Base64 decoded from Vault and returns the file content
    """
    try:
        if read_decoded_content != True:
            return vault_client.read(vault_path)['data']['file']
        else:
            encoded_data = vault_client.read(vault_path)['data']['file']
            file_obj_encode = encoded_data.encode('ascii')
            decoded_data = base64.b64decode(file_obj_encode)
            filedecoded_string = decoded_data.decode('ascii')
            return filedecoded_string
    except Exception as e:
        print("Error in reading config file content from Vault")
        print(e)
        return False


def store_json_file(vault_client, vault_path, file_path):
    """ store_json_file(): Method to store json file content to Vault.
    :param vault_client: HVAC client for Vault
    :param vault_path: Path for Vault
    :param file_path: complete path of the file from local workspace
    :return: None
    """
    try:
        jsn_obj = dict(json.load(open(file_path)))
        vault_client.write(vault_path, **jsn_obj)
        return True
    except Exception as e:
        print('Error writing to vault: %s' % e)
        return False


def read_json_file(vault_client, vault_path):
    """ read_json_file():  Method to read json file content from Vault.
    :param vault_client: HVAC client for Vault
    :param vault_path: vault client path
    :return: data
    """
    try:
        data = vault_client.read(vault_path)['data']
        return data
    except Exception as e:
        print("Unable to read json file %s" % e)
