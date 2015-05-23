#!/usr/bin/env python
#
# Name:			response module
# Description:	response object
#

class Response(object):
	"""this is class Networks, use to view other machine"""
	def __init__(self):
		pass

	def false(self, message):
		return {"response": False, 'message': message}
	def true(self):
		return {"response": True}
	def keepconnect(self, id_machine):
		return {"response": True, 'id_machine': id_machine}	
	def connect(self, lsmachine):
		""" response list mac if same hostname """
		rs = {"response": True, "choice": True, "machine": lsmachine}
		return rs
	def request_connect(self, session, machine):
		rs = {"response": True, "connect": True, "session": session, 'machine': machine}
		return rs
	def udp_hole(self, port):
		rs = {"response": True, "port": port}
		return rs
	def accept_connect(self, session, laddr, lport, addr, port, external, work, dest_port):
		rs = {"response": True, "choice": False, "session": session, "lport" : lport,
		"laddr": laddr, "port": port, "addr": addr, "external": external, "work": work, "destination_port": dest_port}
		return rs