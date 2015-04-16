""" 
	@module jsocket
	Contains JsonSocket json object message passing for client.

	This file is part of the jsocket package.
"""

import base64, hashlib, random, string
from Crypto.PublicKey import RSA
from Crypto.Util import randpool
from Crypto.Cipher import AES
from Crypto import Random
import socket, struct, json, time, pickle
from gshs.config import *
class Secure(object):
	"""docstring for Secure"""
	def __init__(self):
		self.key = False
	def getkey(self):
		code = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])
		self.key = hashlib.sha256(code).digest()
		return self.key
	def hadkey(self):
		if self.key:
			return True
		return False
	def rsakey(self):
		#generate the RSA key
		rand = randpool.RandomPool()
		RSAKey = RSA.generate(2048, rand.get_bytes) 
		RSAPubKey = RSAKey.publickey()
		return RSAKey, RSAPubKey

	def encrypt( self, raw ):
		BS = 16
		pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
		raw = pad(raw)
		iv = Random.new().read( AES.block_size )
		cipher = AES.new( self.key, AES.MODE_CBC, iv )
		return iv + cipher.encrypt( raw )

	def decrypt( self, enc ):
		unpad = lambda s : s[:-ord(s[len(s)-1:])]
		iv = enc[:16]
		cipher = AES.new(self.key, AES.MODE_CBC, iv )
		return unpad(cipher.decrypt( enc[16:] ))

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
		self.secure 	= Secure()
	def set_server(self, port=False):
		if self.tcp:
			self.socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		else:
			self.socket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
		if not port and port != 0:
			self.port 	= SERVER_PORT
			self._bind(self.port)
		else:
			self.port = self._bind(port)
		if self.tcp:
			self._listen()
		return self.port
	def set_socket(self, sock):
		self.socket = sock

	def gethostname(self):
		return socket.gethostname()
	def getpeername(self):
		return self.socket.getpeername()	
	def get_conn(self):
		return self.socket

	def send_obj(self, obj, peer=False):
		msg = json.dumps(obj)
		msg = self.secure.encrypt(msg)
		if self.socket:
			if self.tcp:
				self.socket.send(msg)
				return True
			elif(self.peer):
				if peer:
					self.socket.sendto(peer, msg)
				else:
					self.socket.sendto(self.peer, msg)
				return True
		return False

	def read_obj(self):
		msg = self._read(5120)
		if not self.secure.hadkey():
			key = self.secure.getkey()
			publickey = pickle.loads(msg)
			pkey = publickey.encrypt(key, 32)
			self.socket.send(pkey[0])
			msg = self._read(5120)
		msg = self.secure.decrypt(msg)
		return json.loads(msg)
	def _read(self, size):
		if self.tcp:
			data = self.socket.recv(size)
		else:
			data, self.addr = self.socket.recvfrom(size)
		return data

	def _bind(self, port):
		self.socket.bind( ("", port))
		return self.socket.getsockname()[1]

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