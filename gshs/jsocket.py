""" 
	@module jsocket
	Contains JsonSocket json object message passing for client.

	This file is part of the jsocket package.
	Copyright (C) 2011 by Christopher Piekarski <chris@cpiekarski.com>
	Thank author!
"""
import socket, struct, json, time

from ConfigParser import SafeConfigParser

__CONFIG_FILE__ = "/etc/gshs/gshs.conf"
__SV_SECTION__  = 'Server'
__SV_PORT__ 	= 'Port'
__SV_TIME__		= 'Timeout'
class JsonSocket(object):
	def __init__(self, sk = None):
		parser 			= SafeConfigParser()
		parser.read(__CONFIG_FILE__)
		if sk is None:
			self.socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
			self.port 	= int(parser.get(__SV_SECTION__, __SV_PORT__))
			self._bind()
			self._listen()
		else:
			self.socket = sk
		self._timeout 	= int(parser.get(__SV_SECTION__, __SV_TIME__))


	def send_obj(self, obj):
		msg = json.dumps(obj)
		if self.socket:
			self.socket.send(msg)

	def gethostname(self):
		return socket.gethostname()
	def getpeername(self):
		return self.socket.getpeername()	
	def _read(self, size):
		data = self.socket.recv(size)
		return data

	def read_obj(self):
		msg = self._read(5120)
		return json.loads(msg)

	def _bind(self):
		self.socket.bind( ("",self.port) )

	def _listen(self):
		self.socket.listen(5)
	
	def _accept(self):
		return self.socket.accept()
	def set_timeout(self):
		self.socket.settimeout(self._timeout)

	def accept_connection(self):
		conn, addr = self._accept()
		conn.settimeout(self._timeout)

		return conn


	def close(self):
		self.socket.close()