#########################################################################################################################################################
#    File Name:        Utility.py
#    Description:    File contains list of methods to generated to verify REST API testing using Python.
#    Created By:        Tejeswara Rao Kottapalli
#########################################################################################################################################################

import base64
import logging
from lib.utility import Utility
utilitytest = Utility()


class Headers(object):

    def GenerateHeaders(self, header):
        headers = {}
        if header == 'mdm_provisioned_client':
            username = utilitytest.get_prop_val_by_section('config.properties', 'STATIC', 'mdm_oauthclient')
            password = utilitytest.get_prop_val_by_section('config.properties', 'STATIC', 'mdm_oauthpassword')
            base64Encoding = base64.b64encode(username + ':' + password)
            headerBase64Encoding = 'Basic ' + base64Encoding
            headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json', 'Authorization': headerBase64Encoding, 'api-version': '2'}
        elif header == 'Service_Read':
            apiversion = utilitytest.get_prop_val_by_section('config.properties', 'STATIC', 'api_version')
            accesstoken = 'Bearer ' + utilitytest.get_prop_val_by_section('config.properties', 'RUNTIME',
                                                                          'access_token')
            headers = {'api-version': apiversion, 'Authorization': accesstoken, 'Accept':'application/json'}
        elif header == 'Mdm_boot_login':
            clientid = utilitytest.get_prop_val_by_section('config.properties', 'STATIC', 'mdm_bootclient')
            clientuserpassword = utilitytest.get_prop_val_by_section('config.properties', 'STATIC', 'mdm_bootpassword')
            base64Encoding = base64.b64encode(clientid + ':' + clientuserpassword)
            headerBase64Encoding = 'Basic ' + base64Encoding
            headers = {'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': headerBase64Encoding, 'api-version': '2'}
        else:
            logging.info("Header is Blank")

        return headers
