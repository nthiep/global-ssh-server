#!/usr/bin/env python
#
# Name:			response module
# Description:	response object
#

class Response(object):
	"""this is class Networks, use to view other machine"""
	def __init__(self):
		pass

	def false(self):
		return {"response": False}
	def true(self):
		return {"response": True}
	def login(self, token):
		""" response login status """
		rs = {"response": True, "token": token}
		return rs
	def listmachine(self, lsmachine):
		""" response list machine of user and Networks """
		if len(lsmachine) == 0:
			response = False
		else:
			response = True
		rs = {"response": response, "machine": lsmachine}
		return rs
	def checknat(self, check, port = None):
		rs = {"response": True, "check": check, "port": port}
		return rs
	def connect(self, lsmachine):
		""" response list mac if same hostname """
		rs = {"response": True, "choice": True, "machine": lsmachine}
		return rs
	def portudp(self, port):
		rs = {"response": True, "port": port}
		return rs
	def accept_connect(self, session, laddr, lport, addr, port, external, work):
		rs = {"response": True, "choice": False, "session": session, "lport" : lport,
		"laddr": laddr, "port": port, "addr": addr, "external": external, "work": work}
		return rs