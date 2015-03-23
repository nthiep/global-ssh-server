#!/usr/bin/env python
#
# Name:			response module
# Description:	response object
#

class Response(object):
	"""this is class Networks, use to view other machine"""
	def __init__(self):
		pass
	def listmachine(self, usermac, netmac):
		""" response list machine of user and Networks """
		if usermac:
			if len(usermac) == 0:
				usermac = False
		if netmac:
			if len(netmac) == 0:
				netmac = False
		rs = {"response": True, "usermac": usermac, "netmac": netmac}
		return rs