#!/usr/bin/env python
#
# Name:			request module
# Description:	request class object
#

import socket, json, hashlib, random, time, thread
from bson	import json_util

from django.utils import timezone
from node.models import Machine, Gateway
from oauth2_provider.models import AccessToken
from manage.models import Domain, Workgroup
from .handle import Handle
from .jsocket import JsonSocket
from .response import Response
from .models import Session

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
		self.listpeer = ls_connect()
		self.session  = {}
		self.response = Response()
	def get_request(self, data):
		"""
		return to request type of user
		"""
		return data["request"]

	def keepconnect(self, data, connection):
		mac 	 = data["mac"]
		hostname = data["hostname"]
		platform = data["platform"]
		ip 		 = data["ip"]
		private  = False
		if data["private"]:
			private = True

		if not self.listpeer.check(mac):
			machine, created = Machine.objects.get_or_create(mac=mac, hostname=hostname,\
								platform=platform, ip=ip, private=private)
			connection.none_timeout()
			connection.set_keepalive()
			peer 		= peer_mac(mac, connection)
			self.listpeer.addpeer(peer)
			newhandle 	= Handle(connection, mac, self.listpeer)
			newhandle.start()
			connection.send_obj(self.response.true())
			return False
		return False
	def createtoken(self):
		""" create random api key token"""
		code = random.getrandbits(128)
		return hashlib.sha1(str(code)).hexdigest()



	def check_token(self, token):
		try:
			token = AccessToken.objects.get(token=token)		
			if timezone.now() < token.expires:
				return True
			return False
		except AccessToken.DoesNotExist:
			return False
	def get_machine_domain(self, host=None, macpeer=None, domain=None):
		try:
			if macpeer:
				return Machine.objects.filter(mac=macpeer, domain=domain, private=False)
			elif host:
				return Machine.objects.filter(hostname=host, domain=domain, private=False)
			return False
		except Machine.DoesNotExist:
			print "not machine"
			return False
	def get_machine_workgroup(self, host=None, macpeer=None, workgroup=None):
		try:
			if macpeer:
				return Machine.objects.filter(mac=macpeer, workgroup=workgroup, private=False)
			elif host:
				return Machine.objects.filter(hostname=host, workgroup=workgroup, private=False)
			return False		
		except Machine.DoesNotExist:
			return False


	def _connect_process(self, machine, data, connection):
		addr, port = connection.getpeername()
		source = Machine.objects.get(mac=data["mac"])
		if source.gateway is None:
			nat = 'D'
			sym = False
		else:
			nat = source.gateway.nat
			sym = source.gateway.sym
		session, created 	= Session.objects.get_or_create(laddr=data["laddr"], lport=data["lport"], 
			addr = addr, port = port, nat = nat, sym = sym, sport = data["sport"])
		self.session[session.id] = connection
		connp = self.listpeer.getconnect(machine[0].mac)
		if not connp:
			return self.response.false()
		connp.send_obj({"response": "bind", "session": session.id})
		time.sleep(10)
		try:
			del self.session[session.id]
		except:
			pass
		return False
	def connect(self, data, connection):
		""" request connect to other machine """
		print data
		token 	 = data["token"]
		mac 	 = data["mac"]
		peer	 = data["peer"]
		macpeer  = data["macpeer"]
		workgroup_id = data["workgroup_id"]
		workgroup_secret = data["workgroup_secret"]
		if token and self.check_token(token):
			try:
				access = AccessToken.objects.get(token=token)
			except AccessToken.DoesNotExist:
				return self.response.false()

			machine = self.get_machine_domain(peer, macpeer, access.user)
		elif workgroup_id:
			try:
				workgroup = Workgroup.objects.get(id=workgroup_id, secret_key=workgroup_secret)
			except Workgroup.DoesNotExist:
				return self.response.false()

			machine = self.get_machine_workgroup(peer, macpeer, workgroup)
		else:
			machine = False
		if not machine:
			return self.response.false()

		if machine.count() == 1:
			return self._connect_process(machine, data, connection)
		else:
			return self.response.connect(machine)
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
		session_id = data["session"]
		try:
			session = Session.objects.get(id=session_id)
		except Session.DoesNotExist:
			return False
		print "linked request session: %s" % session_id
		machine = Machine.objects.get(mac=data["mac"])
		sport = session.sport
		nata = session.nat
		syma = session.sym
		if machine.gateway is None:
			natb='D'
			symb=False
		else:
			natb = machine.gateway.nat
			symb = machine.gateway.sym

		worka, workb = self.connect_response(nata, natb, syma, symb)
		connp = self.session[session_id]
		addr, port = connection.getpeername()
		p = self.response.accept_connect(session_id, data["laddr"],
		 	data["lport"], addr, port, session.addr, worka)
		q = self.response.accept_connect(session_id, session.laddr,
			session.lport, session.addr, session.port, addr, workb, sport)
		connp.send_obj(p)
		connection.send_obj(q)
		connp.close()
		connection.close()
		del self.session[session_id]
		return False
		
	def checknat_symmetric(self, connection):
		sock = JsonSocket(JsonSocket.UDP)
		port = sock.set_server(0)
		send_obj	= self.response.checknat(True, port, True)	
		connection.send_obj(send_obj)
		connection.close()
		data = sock.read_obj()
		return sock
	def checknat_listen(self, connection):
		sock 	= JsonSocket(JsonSocket.TCP)
		port = sock.set_server(0)
		sock.set_timeout()
		send_obj	= self.response.checknat(True, port)
		connection[0].send_obj(send_obj)
		connection[0].close()
		c = sock.accept_connection()
		conn = JsonSocket(JsonSocket.TCP)
		conn.set_socket(c)
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

		try:
			machine	   = Machine.objects.get(mac=mac)
		except Machine.DoesNotExist:
			return self.response.checknat(False)
		addr, port = connection.getpeername()
		conn = []
		conn.append(connection)
		_sym = False
		nat = self.checknat_function(conn, laddr, lport, addr, port)
		if nat in ['S', 'A', 'DA']:
			_i = 0
			_sport = False
			_conn = conn[0]
			while _i < 3:
				_conn = self.checknat_symmetric(_conn)
				ad, po = _conn.addr
				if _sport and po != _sport:
					_sym = True
					break
		if nat == 'D':
			return self.response.checknat(False)
		gateway, created = Gateway.objects.get_or_create(ip=addr)
		machine.gateway = gateway
		machine.save()
		if created:
			gateway.nat = nat 
			gateway.sym = _sym
			gateway.save()
		send_obj = self.response.checknat(False)
		conn[0].send_obj(send_obj)
		conn[0].close()
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
		session_id = data["session"]
		if self._check_session(session_id):
			print "have session"
			conna = connection.get_conn()
			connb = self.session[session_id]
			conna.none_timeout()
			connb.none_timeout()
			thread.start_new_thread(self._relay_forward, (session_id, conna, connb))			
			thread.start_new_thread(self._relay_forward, (session_id, connb, conna))
			del self.session[session_id]
			print "start thread relay %s" %session_id
		else:
			print "add session relay %s" %session_id
			self.session[session_id] = connection.get_conn()
		return False
	def udp_hole(self, data, connection):
		session_id = data["session"]
		try:
			session = Session.objects.get(id=session_id)
		except Session.DoesNotExist:
			return False
		if self._check_session(session_id):
			port = self.session[session_id]
			del self.session[session_id]
			return self.response.portudp(port)
		else:
			udp = JsonSocket(JsonSocket.UDP)
			port = udp.set_server(0)
			self.session[session_id] = port
			thread.start_new_thread(self.udp_connect, (session_id, udp))
			return self.response.portudp(port)

	def udp_connect(self, session_thread, udp):
		while True:
			data = udp.read_obj()
			addr = udp.getpeername()
			print "connection from udp  %s:%d" % addr 
			try:
				session_id = data["session"]
				host, port = addr
				if session_id != session_thread:
					continue
				try:
					session = Session.objects.get(id=session_id)
				except Session.DoesNotExist:
					continue
				if not session.udp:
					session.udp = True
					session.host = host
					session.port = port
					session.save()
					continue
				else:
					udp.send_obj({"host": host, "port": port}, (session.udphost, int(session.udpport)))
					udp.send_obj({"host": session.udphost, "port": session.udpport}, addr)
					print "linked session %s" % session_id
					break
			except:
				break
		udp.close()