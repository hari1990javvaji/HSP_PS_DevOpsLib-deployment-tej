**Project Title :**

#MyVault#

    Secures, stores, and tightly controls access to tokens, passwords, certificates, API keys, and other secrets in
    modern computing. Vault handles leasing, key revocation, key rolling, and auditing. Through a unified API,
    users can access an encrypted Key/Value store and network encryption-as-a-service, or generate AWS IAM/STS
    credentials, SQL/NoSQL databases, X.509 certificates, SSH credentials, and more.

**Features**
    
    1. CF Credentials in Vault
    2. Config File in Vault - Entire Config File is stored in Vault with Base64 Encode and Decode
    3. Read Config File from Vault - No Storage in Filesystem/Bitbucket Repo
    4. Pub Key File(RSA) in Vault - Entire Pub File is stored in Vault with Base64 Encode and Decode    
  
**Prerequisites and Installation**

    1. Install Python 2.7
	3. pip install hvac
	4. pip install cloudfoundry_client==0.0.22

**How to Use**

** Following list steps for one time creation **

**Step 1:** Create a vault service in the respective CF Space. Go to Org, Space through command line and run the following commands. Vault Service name and Key can be anything

**Step 2:** Create Cloudfoundry service

`        Command: cf create-service hsdp-vault vault-us-east-1 <VaultServiceInstance>`
        
**Step 3:** Create service Key

`        Command: cf create-service-key <VaultServiceInstance> <MyKey>`
        
**Step4:** If you want to know the vault keys, run the following. This is for your information

`        Command: cf service-key <ValutServiceName> <MyKey>`

	        
**Step4:** Following Step to upload file to Vault and also download from vault. 

python read_write_vault.py -h
usage: read_write_vault.py [-h]
                           cf_user cf_pwd cf_org cf_space cf_vault_service
                           cf_url file_path vault_path {w,write,r,read}
                           {binary,json,any}

Vaultification of Service Secrets:

positional arguments:
  cf_user_name       Provide CF User Name
  cf_password        Provide CF Password
  cf_org       		 Provide CF Org Name
  cf_space           Provide CF Space
  vault_service_name Provide CF Vault Service Name
  cf_url             Provide CF URL. Example: api.cloud.pcftest.com
  file_path          Provide file you want to upload to vault or download to a local location
  vault_path         Provide a path where to upload or download from vault. Example: config
  {w,write,r,read}   Provide one of the following options:
                     w or write for writing configurations in vault
                     r or read for reading configurations from vault and store in file_path location
  {binary,json,any}  Provide file type to upload/download. Example: binary or json or any

optional arguments:
  -h, --help         show this help message and exit


Example:
**For Write to Vault:**

    python read_write_vault.py <cf_user_name> <cf_password> <cf_org> <cf_space> <vault_service_name> api.cloud.pcftest.com <local_file_full_path> <vaultpath> w 'any'

**For Read from Vault:**

    python read_write_vault.py <cf_user_name> <cf_password> <cf_org> <cf_space> <vault_service_name>  api.cloud.pcftest.com <local_file_full_path> <vaultpath> r 'any'


**Acknowledgments**

    https://healthsuite.atlassian.net/wiki/spaces/HPO/pages/125944551/Using+the+Vault+CLI
    https://github.com/ianunruh/hvac
    