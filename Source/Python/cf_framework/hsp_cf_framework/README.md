README.md

Driver script is used to deploy application on cloud foundry.
It can be invoked as follows
```

usage: auto_deploy.py [-h] CF_API_HOST CF_LOGIN_HOST CF_ORG CF_SPACE CF_USERNAME CF_PASSWORD CSV_FILE LOG_LEVEL RELEASE_VERSION

positional arguments:
  CF_API_HOST      Provide cf api HOST
  CF_LOGIN_HOST    Provide cf login HOST
  CF_ORG           Provide cf org
  CF_SPACE         Provide cf space
  CF_USERNAME      Provide cf user name
  CF_PASSWORD      Provide cf password in quotes
  CSV_FILE         Provide csv file name
  LOG_LEVEL        Provide logging level as info or debug or error
  RELEASE_VERSION  provide release version. Example 1.0.0.0

optional arguments:
  -h, --help       show this help message and exit


Example
    python auto_deploy.py api.cloud.pcftest.com login.cloud.pcftest.com ENG-CICD system_team_poc tkottapalli XXXXXXXXXX smoke.csv info 1.0.0.0
 ```


Following Steps are optional as part of deployment. If it requires, then only perform
```
This framework also covers vault service creation, bind with a key and upload the configuration file to vault. You can also download from vault
1. Before running vault script, please update the following from configurations\release folder location
	a. update config.json with required values
	b. update vaultconfig.yaml
	
2. For creation of vault service and upload the config.json content, run the following command
   python createsetupvault.py w
   
3. For reading configuration which is uploaded in vault, run the following command.
   python createsetupvault.py r
   
python create_vault_setup.py -h
usage: create_vault_setup.py [-h] [-c CONF] CF_USER CF_PWD {w,r}

Vaultification - Deployment Configuration

positional arguments:
  CF_USER               Provide CF User Name
  CF_PWD                Provide CF Password
  {w,r}                 Provide one of the following options:
                        w for writing deployment configurations in vault
                        r for reading deployment configurations from vault
   
