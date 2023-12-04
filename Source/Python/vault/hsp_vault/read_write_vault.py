"""Read Write vault scripts for uploading/downloading the files"""
from argparse import ArgumentParser
from argparse import RawTextHelpFormatter
import VaultOperations
import VaultServiceCreds


def parse_args():
    """This function is to parse the arguments from command line"""
    parser = ArgumentParser( description='Vaultification of Service Secrets:',
                             formatter_class=RawTextHelpFormatter )

    parser.add_argument( "cf_user_name",
                         help="Provide CF User Name" )
    parser.add_argument( "cf_password",
                         help="Provide CF Password" )
    parser.add_argument( "cf_org",
                         help="Provide CF Org Name" )
    parser.add_argument( "cf_space",
                         help="Provide CF Space" )
    parser.add_argument( "vault_service_name",
                         help="Provide CF Vault Service Name" )
    parser.add_argument( "cf_url",
                         help="Provide CF URL. Example: api.cloud.pcftest.com" )
    parser.add_argument( "file_path",
                         help="Provide file you want to upload to vault or "
                              "download to a local location" )
    parser.add_argument( "vault_path",
                         help="Provide a path where to upload or download from vault. "
                              "Example: config" )
    parser.add_argument( "option",
                         choices=["w", "write", "r", "read"],
                         help="Provide one of the following options:\n"
                              "w or write for writing configurations in vault\n"
                              "r or read for reading configurations from vault and "
                              "store in file_path location" )
    parser.add_argument( "file_type",
                         choices=["binary", "json", "any"],
                         help="Provide file type to upload/download."
                              " Example: binary or json or blank value" )

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    key = VaultServiceCreds.get_vault_service_credentials( 'https://' + args.cf_url,
                                                           args.cf_user_name,
                                                           args.cf_password,
                                                           args.cf_org,
                                                           args.cf_space,
                                                           args.vault_service_name, None
                                                           )

    client = VaultOperations.vault_client_create( key['endpoint'],
                                                  key['role_id'],
                                                  key['secret_id'] )

    if args.option.lower() == 'w' or args.option.lower() == 'write':
        print( 'To Write File in Vault' )

        if args.file_type.lower() == 'binary':
            VaultOperations.store_binary_config_file( client,
                                                      key['service_secret_path'].strip(
                                          'v1/' ) + '/' + args.vault_path.strip(),
                                                      args.file_path.strip() )
        elif args.file_type.lower() == 'json':
            VaultOperations.store_json_file( client,
                                             key['service_secret_path'].strip(
                                 'v1/' ) + '/' + args.vault_path.strip(),
                                             args.file_path.strip() )
        else:
            VaultOperations.store_config_file( client,
                                               key['service_secret_path'].strip(
                                   'v1/' ) + '/' + args.vault_path.strip(),
                                               args.file_path.strip() )
        print( 'File is Uploaded. Vault Path: ' + args.vault_path )
    elif args.option.lower() == 'r' or args.option.lower() == 'read':
        print( 'To Read file from Vault and store in local path.' )

        if args.file_type.lower() == 'binary':
            config_obj = VaultOperations.read_config_file( client,
                                                           key['service_secret_path'].strip(
                                               'v1/' ) + '/' + args.vault_path.strip() )
            fs = open( args.file_path.strip(), 'wb' )
            fs.write( bytearray(config_obj, encoding ="utf-8") )

            fs.close()
        elif args.file_type.lower() == 'json':
            config_obj = VaultOperations.read_json_file( client,
                                                         key['service_secret_path'].strip(
                                             'v1/' ) + '/' + args.vault_path.strip() )
            fs = open( args.file_path.strip(), 'w' )
            VaultServiceCreds.json.dump( config_obj, fs, indent=2 )
            fs.close()
        else:
            config_obj = VaultOperations.read_config_file( client,
                                                           key['service_secret_path'].strip(
                                               'v1/' ) + '/' + args.vault_path.strip() )
            fs = open( args.file_path.strip(), 'w' )
            fs.write( config_obj )
            fs.close()
        print( 'File is Downloaded. File Location: ' + args.file_path.strip() )
        print( '' )


if __name__ == '__main__':
    main()
