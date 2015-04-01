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
class JsonSocket(object):
	def __init__(self):
		self._timeout 	= SERVER_TIMEOUT
		self.public = False
		self.key 	= False

	def set_server(self):
		self.socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		self.port 	= SERVER_PORT
		self._bind()
		self._listen()
	def set_socket(self, sock):
		self.socket = sock
	def set_port(self):
		self.socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		self.sock.bind(("", 0))
		addr, port = self.sock.getsockname()
		self._listen()
		return port
	def get_conn(self):
		return self.socket
	def getpeername(self):
		return self.socket.getpeername()
	def send_obj(self, obj):
		msg = json.dumps(obj)
		msg = self.encrypt(msg)
		if self.socket:
			self.socket.send(msg)
	def send(self, msg):
		self.socket.send(msg)

	def gethostname(self):
		return socket.gethostname()
	def getpeername(self):
		return self.socket.getpeername()	
	def _read(self, size):
		data = self.socket.recv(size)
		return data
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
	def read_obj(self):
		msg = self._read(5120)
		if not self.key:
			code = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])
			self.key = hashlib.sha256(code).digest()
			self.publickey = pickle.loads(msg)
			pkey = self.publickey.encrypt(self.key, 32)
			self.socket.send(pkey[0])
			msg = self._read(5120)
		msg = self.decrypt(msg)
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