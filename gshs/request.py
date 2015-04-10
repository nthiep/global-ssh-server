#!/usr/bin/env python
#
# Name:			request module
# Description:	request class object
#

import socket, json, hashlib, random, time, thread
from gshs 	import Database
from gshs 	import Users
from gshs 	import Machines
from gshs 	import APIusers
from gshs  	import APInets
from gshs 	import Networks
from gshs  	import Handle
from gshs	import Response
from gshs	import Sessions
from gshs 	import JsonSocket
from bson	import json_util

class peer_mac(object):
	""" save list connection handle"""
	def __init__(self, mac, connection):
		self.mac = mac
		self.connection = connection

class ls_connect(object):
	"""docstring for ls_connect"""
	def __init__(self):
		self.peer = []

	def addpeer(self, peer):
		self.peer.append(peer)

	def getconnect(self, mac):
		for p in self.peer:
			if p.mac == mac:
				return p.connection
		return False
	
	def remove(self, mac):
		for p in self.peer:
			if p.mac == mac:
				self.peer.remove(p)
	def check(self, mac):
		for p in self.peer:
			if p.mac == mac:
				return True
		return False


class Request(object):
	"""docstring for Request"""
	def __init__(self):
		try:
			conn = Database()
			self.database = conn.connect()
			self.datatype = conn.database
		except Exception, e:
			print e
			raise Exception("Database Error: can connect to database")
		self.listpeer = ls_connect()
		self.session  = {}
		self.response = Response()
	def get_request(self, data):
		"""
		return to request type of user
		"""
		getconnect = False
		if data["request"] in ['keepconnect', 'connect', 'accept_connect',
			 'checknat', 'relay', 'udp_hole']:
			getconnect = True
		return data["request"], getconnect

	def keepconnect(self, data, connection):
		mac 	 = data["mac"]
		hostname = data["hostname"]
		platform = data["platform"]
		machine 	= Machines(self.database, self.datatype)
		machine.addmachine(mac, hostname, platform)
		if not self.listpeer.check(mac):
			peer 		= peer_mac(mac, connection)
			self.listpeer.addpeer(peer)
			newhandle 	= Handle(connection, mac, self.listpeer)
			newhandle.start()
			return True
		return False
	def createtoken(self):
		""" create random api key token"""
		code = random.getrandbits(128)
		return hashlib.sha1(str(code)).hexdigest()
	def login(self, data):
		"""
		request login of client
		"""
		username = data["username"]
		passwork = data["passwork"]
		mac 	 = data["mac"]
		user = Users(self.database, self.datatype)		
		pswd = hashlib.sha1(passwork).hexdigest()
		if user.checkauth(username, pswd):
			apikey = user.getapikey(username)
			return self.response.login(apikey)
		return self.response.false()

	def register(self, data):
		"""
		request login of client
		"""
		username = data["username"]
		passwork = data["passwork"]
		fullname = data["fullname"]
		email	 = data["email"]
		website	 = data["website"]
		apikey 	 = self.createtoken()
		user = Users(self.database, self.datatype)
		pswd = hashlib.sha1(passwork).hexdigest()
		if user.adduser(username, pswd, fullname, email, website, apikey):
			return self.response.true()
		return self.response.false()

	def authuser(self, data):
		""" authentication of api key user """
		apikey   = data["apikey"]
		mac 	 = data["mac"]
		user 	 = Users(self.database, self.datatype)
		if user.checkapikey(apikey):
			apiuser  = APIusers(self.database, self.datatype)
			username = user.getuser(apikey)
			apiuser.addapimac(username, mac)
			return self.response.true()
		return self.response.false()

	def authnetwork(self, data):
		""" request of add network """
		netkey  	= data["netkey"]
		mac 		= data["mac"]
		nw 			= Networks(self.database, self.datatype)
		i = 0
		for k in netkey:
			if nw.checknetwork(k[:24], k[24:]):
				api = APInets(self.database, self.datatype)
				if api.addapi(mac, k[:24]):
					i += 1
		return str(i) + '/' + str(len(netkey))

	def createnetwork(self, data):
		""" add network """
		mac 	= data["mac"]
		netname = data["netname"]
		netkey  = self.createtoken()
		nw 		= Networks(self.database, self.datatype)
		netid = nw.addnetwork(mac, netname, netkey)
		return netid + netkey

	def _get_listmac(self, mac, apikey):
		""" get list peer machine of mac """
		lsmu = []
		lsmn = []
		if apikey:
			user 	 = Users(self.database, self.datatype)
			apiuser = APIusers(self.database, self.datatype)
			username   = user.getuser(apikey)
			lsmu = apiuser.listmac(username)
		apinet = APInets(self.database, self.datatype)
		lsmn = apinet.listmac(mac)
		lsmac = lsmu + lsmn  
		return lsmac
	def listmachine(self, data):
		""" response all machine of client """
		mac  	 = data["mac"]
		apikey	 = data["apikey"]
		lsmac 	 = self._get_listmac(mac, apikey)  
		machine	 = Machines(self.database, self.datatype)	
		lsmachine = []
		if len(lsmac) != 0:
			lsmachine   = list(machine.listmachine(lsmac))
		return self.response.listmachine(lsmachine)

	def renetwork(self, data):
		""" remove network of machine """
		netkey   = data["netkey"]
		mac 	 = data["mac"]
		nw 		 = Networks(self.database, self.datatype)
		apin 	 = APInets(self.database, self.datatype)
		for k in netkey:
			if nw.checknetwork(k[:24], k[24:]):
				if nw.checkadmin(mac, k[:24]):
					apin.removenet(k[:24])
					nw.removenet(k[:24])
				else:
					apin.renetmac(mac, k[:24])
				return self.response.true()
		return self.response.false()

	def _connect_process(self, mac, macpeer, data, connection):
		ss = self.createtoken()
		ses 	= Sessions(self.database, self.datatype)
		self.session[ss] = connection
		addr, port = connection.getpeername()
		machine	 = Machines(self.database, self.datatype)
		peer = machine.getmachine(mac)
		ses.addsession(ss, data["laddr"], data["lport"], addr, port, peer["nat"])
		connp = self.listpeer.getconnect(macpeer)
		if not connp:
			return
		connp.send_obj({"response": "bind", "session": ss})
		time.sleep(10)
		try:
			del self.session[ss]
		except:
			pass
	def connect(self, data, connection):
		""" request connect to other machine """
		apikey   = data["apikey"]
		mac 	 = data["mac"]
		peer	 = data["peer"]
		macpeer  = data["macpeer"]
		lsmac 	 = self._get_listmac(mac, apikey)
		if len(lsmac) != 0:
			if macpeer:
				if macpeer in lsmac:
					self._connect_process(mac, macpeer, data, connection)
					return False
			else:	
				machine	 = Machines(self.database, self.datatype)	
				lsmachine   = list(machine.listhost(lsmac, peer))
				if len(lsmachine) == 1:
					self._connect_process(mac, lsmachine[0]["mac"], data, connection)
				elif len(lsmachine) > 1:
					return self.response.connect(lsmachine)
		return self.response.false()

	def connect_response(self, nata, natb, syma, symb):
		""" response type of connect """
		_direct 	= "DRT"		#for a: connect direct when b on the internet
		_lssv 		= "LSV"		#for b: listen on port if ssh port change
		_listen 	= "LIS"		#for a: listen port when a is symmetric nat and b is direct
		_revers 	= "REV" 	#for b: connect direct when a on the internet
		_hole		= "HOL"		#for a,b: connect via hole punching, a and b is cone nat
		_mhole		= "MHO"		#for a, b: connect via multi hole punching with ascending port
		_mholed		= "MHD"		#for a, b: connect via multi hole punching with deascending port
		_uhole		= "UHO"		#for a, b: connect via udp hole punching
		_relay 		= "REL"		#for a, b: connect use relay server, with symmetric nat


		# connect table of different nat
		#---------------------------------------------------------------------
		#			| Drect | Full cone | ascending or desc | symmetric
		# Direct 	| _dir 	| reversal 	| reversal	 		| reversal
		# Full cone | _dir 	| hole 		| multi hole 		| udp hole
		# D/ascen.. | _dir 	| multi hole| udp hole 			| relay
		# Symmetric	| _dir 	| udp hole 	| relay 			| relay
		# --------------------------------------------------------------------
		# if connect not work, it will connect via udp hole --> relay
		#

		if natb == 'D':
			return _direct, _lssv
		"""
		if nata == 'D':
			return _listen, _revers
		"""
		#this is a test
		if nata == 'D':
			return _uhole, _uhole
		
		if nata == 'F':
			if natb == 'F':
				return _hole, _hole
			if natb == 'A':
				return _mhole, _hole
			if natb == 'DA':
				return _mholed, _hole
			if natb == 'S':
				return _uhole, _uhole
		if nata == 'A' or nata == 'DA':
			if natb == 'F':
				if nata == 'A':
					return _hole, _mhole
				if nata == "DA":
					return _hole, _mholed
			if natb == 'A' or natb == 'DA':
				return _uhole
			if natb == 'S':
				if not syma or not symb:
					return _uhole, _uhole
				return _relay, _relay
		if nata == 'S':
			if natb == 'F':
				return _uhole, _uhole
			if not syma or not symb:
				return _uhole, _uhole
			return _relay, _relay


	def accept_connect(self, data, connection):
		ses 	= Sessions(self.database, self.datatype)
		if ses.checksession(data["session"]):
			print "linked request session: %s" % data["session"]
			machine = Machines(self.database, self.datatype)
			mc 	 = machine.getmachine(data["mac"])
			peer = ses.getsession(data["session"])
			nata = peer["nat"]
			syma = peer["issym"]
			natb = mc["nat"]
			symb = mc["issym"]

			worka, workb = self.connect_response(nata, natb, syma, symb)
			connp = self.session[data["session"]]
			addr, port = connection.getpeername()
			p = self.response.accept_connect(data["session"], data["laddr"],
			 	data["lport"], addr, port, peer["addr"], worka)
			q = self.response.accept_connect(data["session"], peer["laddr"],
				peer["lport"], peer["addr"], peer["port"], addr, workb)
			connp.send_obj(p)
			connection.send_obj(q)
			connp.close()
			connection.close()
			del self.session[data["session"]]
		return False
	def checknat_symmetric(self, connection):
		sock = JsonSocket(JsonSocket.UDP)
		port = sock.set_server(0)
		send_obj	= self.response.checknat(True, port, True)	
		connection.send_obj(send_obj)
		connection.close()
		conn = sock.read_obj()
		conn = s.set_socket(conn)
		return conn
	def checknat_listen(self, connection):
		sock 	= JsonSocket(JsonSocket.TCP)
		port = sock.set_server(0)
		sock.set_timeout()
		send_obj	= self.response.checknat(True, port)
		connection[0].send_obj(send_obj)
		connection[0].close()
		conn = sock.accept_connection()
		s = JsonSocket(JsonSocket.TCP)
		conn = s.set_socket(conn)
		connection[0]= conn
		return connection

	def checknat_function(self, connection, laddr, lport, addr, port):
		if addr == laddr:
			return 'D'
		else:
			if lport == port:
				return 'F'
			else:
				_i 		= 0
				_asc 	= 0
				_desc 	= 0
				while _i < 3:
					connection = self.checknat_listen(connection)
					ad, nport = connection[0].getpeername()
					ab = nport - port
					if abs(ab) > 10:
						return 'S'
						break
					else:
						if ab > 0:
							_asc +=1
						else:
							_desc +=1
						port = nport
						_i +=1				
				if _asc >0 and _desc >0:
					return 'S'
				if _asc:
					return 'A'
				else:
					return 'DA'
	def checknat(self, data, connection):
		""" check machine nat type """
		mac 	= data["mac"]
		laddr 	= data["laddr"]
		lport 	= data["lport"]

		addr, port = connection.getpeername()
		machine	   = Machines(self.database, self.datatype)
		if machine.checkmachine(mac):
			conn = []
			conn.append(connection)
			_issym = False
			_conn = conn[0]
			nat = self.checknat_function(conn, laddr, lport, addr, port)
			if nat in ['S', 'A', 'DA']:
				_i = 0
				_sport = False
				while _i < 3:
					_conn = self.checknat_symmetric(_conn)
					ad, po = _conn.getpeername()
					if _sport and po != _sport:
						_issym = True
						break
			machine.editnat(mac, nat, _issym)
			send_obj = self.response.checknat(False)
			_conn.send_obj(send_obj)
			_conn.close()
		return False

	def _relay_forward(self, session, source, destination):
		string = ' '
		while string:
			try:				
				string = source.recv(1024)
				if string:
					destination.sendall(string)
				else:
					print "close bind"
					source.shutdown(socket.SHUT_RD)
					destination.shutdown(socket.SHUT_WR)
			except Exception as e:
				print "Exception forward bind", e
				break
		try:
			del self.session[session]
		except:
			pass
	def _check_session(self, session):
		try:
			self.session[session]
			return True
		except:
			pass
		return False 
	def relay(self, data, connection):
		ses = data["session"]
		if self._check_session(ses):
			print "have session"
			conna = connection.get_conn()
			connb = self.session[ses]
			conna.settimeout(None)
			connb.settimeout(None)
			thread.start_new_thread(self._relay_forward, (ses, conna, connb))			
			thread.start_new_thread(self._relay_forward, (ses, connb, conna))
			del self.session[ses]
			print "start thread relay"
		else:
			print "add session relay"
			self.session[ses] = connection.get_conn()
		return False
	def udp_hole(self, data, connection):
		ses = data["session"]
		if self._check_session(ses):
			port = self.session[ses]
			del self.session[ses]
			return self.response.portudp(port)
		else:
			udp = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
			udp.bind(("", 0))
			addr, port = udp.getsockname()
			self.session[ses] = port
			thread.start_new_thread(self.udp_connect, (ses, udp))
			return self.response.portudp(port)

	def udp_connect(self, session, udp):
		ses = Sessions(self.database, self.datatype)
		while True:
			data, addr = udp.recvfrom(1024)
			print "connection from udp  %s:%d" % addr 
			try:
				data = json.loads(data)
				session = data["session"]
				host, port = addr

				peer = ses.getudpsession(session)
				if not peer:
					ses.addudpsession(session, host, port)
				else:
					udp.sendto(json.dumps({"host": host, "port": port}), (peer["addr"], int(peer["port"])))
					udp.sendto(json.dumps({"host": peer["addr"], "port": peer["port"]}), addr)
					print "linked session %s" % session
					break
			except:
				break
		udp.close()
