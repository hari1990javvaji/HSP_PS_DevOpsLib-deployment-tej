"""
# ##########################################################################################################
#	File Name:		Utility.py
#	Description:	File contains list of methods to generated to verify REST API testing using Python.
#	Created By:		Tejeswara Rao Kottapalli		 
# ##########################################################################################################
"""

import os
import hmac
import hashlib
from base64 import b64encode


class Signature(object):

	def create_hmac(self, data, secret):
		h = hmac.new(secret, digestmod=hashlib.sha256)
		h.update(data)
		return h.digest()

	def createSignature(self, secret_key_prefix, secretKey, sharedKey):    
		appSignLst = []
		sign_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
		secret = ''.join([secret_key_prefix, secretKey])
		sig = self.create_hmac(b64encode(sign_time), secret)
		sig_header = ("HmacSHA256;Credential:{0};SignedHeaders:SignedDate;Signature:{1}".format(sharedKey, b64encode(sig)))
		appSignLst.append(sig_header)    
		appSignLst.append(sign_time)
		return appSignLst

	def AppSignatures(self, command):
		appSignLst = []
		p = os.popen(command)		
		processOutput = p.read()		
		print (processOutput)
		
		splitOutputVal = processOutput.split("SignedDate:")
		if len(splitOutputVal) == 2:
			signatureWithName = splitOutputVal[0]
			signDate = splitOutputVal[1].strip()
			splitSignature = signatureWithName.split("Signature:")
			if len(splitSignature) == 2: 
				signatureName = splitSignature[0].strip()
				signatureValue = splitSignature[1].strip()			
				appSignLst.append(signatureValue)
				appSignLst.append(signDate)								
			else:
				appSignLst.append('False')
				appSignLst.append(signDate)				
		else:
			appSignLst.append('False')
			appSignLst.append('False')
		
		return appSignLst
