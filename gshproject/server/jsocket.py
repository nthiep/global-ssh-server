""" 
	@module jsocket
	Contains JsonSocket json object message passing for client.

	This file is part of the jsocket package.
"""

import base64, hashlib, random, string
import socket, struct, json, time, pickle
from .config import SERVER_PORT, SERVER_TIMEOUT, AFTER_IDLE, INTERVAL, MAX_FAILS
class JsonSocket(object):
	## defined variable
	TCP = 'TCP'
	UDP = 'UDP'
	def __init__(self, protocol, timeout=SERVER_TIMEOUT):
		self.tcp 		= False
		if protocol == 'TCP':
			self.tcp 	= True
		self._timeout 	= timeout
		self.peer		= None
	def set_server(self, port=None):
		if self.tcp:
			self.socket_obj = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		else:
			self.socket_obj= socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
		if port is None:
			self.port 	= SERVER_PORT
			self._bind(self.port)
		else:
			self.port = self._bind(port)
		if self.tcp:
			self._listen()
		return self.port
	def set_socket(self, sock):
		self.socket_obj= sock

	def gethostname(self):
		return socket.gethostname()
	def getpeername(self):
		return self.socket_obj.getpeername()	
	def get_conn(self):
		return self.socket_obj

	def set_keepalive(self, after_idle_sec=AFTER_IDLE, interval_sec=INTERVAL, max_fails=MAX_FAILS):
	    """Set TCP keepalive on an open socket.

	    It activates after AFTER_IDLE second (after_idle_sec) of idleness,
	    then sends a keepalive ping once every INTERVAL seconds (interval_sec),
	    and closes the connection after MAX_FAILS failed ping (max_fails), or 15 seconds
	    """
	    self.socket_obj.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
	    self.socket_obj.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
	    self.socket_obj.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
	    self.socket_obj.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)



	def send_obj(self, obj, peer=False):
		msg = json.dumps(obj)
		if self.socket_obj:
			if self.tcp:
				self.socket_obj.send(msg)
				return True
			elif peer:
				self.socket_obj.sendto(msg, peer)
				return True
			elif self.peer:
				self.socket_obj.sendto(msg, self.peer)
				return True
		return False

	def read_obj(self):
		msg = self._read(5120)
		try:
			return json.loads(msg)
		except:
			raise Exception('Request not Accept!')
	def _read(self, size):
		if self.tcp:
			data = self.socket_obj.recv(size)
		else:
			data, self.addr = self.socket_obj.recvfrom(size)
		if data:
			return data
		raise Exception('Socket Disconnect!')

	def _bind(self, port):
		self.socket_obj.bind( ("", port))
		return self.socket_obj.getsockname()[1]

	def _listen(self):
		self.socket_obj.listen(5)
	
	def _accept(self):
		return self.socket_obj.accept()
	def set_timeout(self):
		self.socket_obj.settimeout(self._timeout)

	def none_timeout(self):
		self.socket_obj.settimeout(None)

	def accept_connection(self):
		conn, addr = self._accept()
		conn.settimeout(self._timeout)
		return conn

	def close(self):
		self.socket_obj.close()