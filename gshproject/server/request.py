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
		self.remove(peer.mac)
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
			ippub = connection.getpeername()[0]		
			gateway, created = Gateway.objects.get_or_create(ip=ippub)
			machine, created = Machine.objects.get_or_create(mac=mac)
			machine.hostname = hostname
			machine.platform = platform
			machine.ip 		 = ip
			machine.gateway  = gateway
			machine.private  = private
			machine.save()
			connection.none_timeout()
			connection.set_keepalive()
			peer 		= peer_mac(mac, connection)
			self.listpeer.addpeer(peer)
			newhandle 	= Handle(connection, machine, self.listpeer)
			newhandle.start()
			connection.send_obj(self.response.keepconnect(machine.id))
			return False
		return self.response.false()
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
	def get_machine_domain(self, host=None, mac=None, domain=None):
		try:
			if macpeer:
				return Machine.objects.filter(mac=mac, domain=domain, private=False)
			elif host:
				return Machine.objects.filter(hostname=host, domain=domain, private=False)
			return False
		except Machine.DoesNotExist:
			print "not machine in domain"
			return False
	def get_machine_workgroup(self, host=None, mac=None, workgroup=None):
		try:
			if macpeer:
				return Machine.objects.filter(mac=mac, workgroup=workgroup, private=False)
			elif host:
				return Machine.objects.filter(hostname=host, workgroup=workgroup, private=False)
			return False		
		except Machine.DoesNotExist:
			print "not machine in workgroup"
			return False

	def _check_ismac(self, hostname):
		if re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", hostname.lower()):
			return True
		return False
	def _connect_process(self, machine, data, connection):
		addr, port = connection.getpeername()
		try:
			source = Machine.objects.get(id=data["id_machine"])
		except:
			return self.response.false()
		nat = source.nat
		nat_tcp = source.nat_tcp
		session, created 	= Session.objects.get_or_create(laddr=data["laddr"], lport=data["lport"], 
			addr = addr, port = port, nat = nat, nat_tcp=nat_tcp, dest_port = data["destination_port"])
		self.session[session.id] = connection
		connp = self.listpeer.getconnect(machine[0].mac)
		if not connp:
			return self.response.false()
		connp.send_obj({"response": "bind", "session": session.id, 'machine': source.mac})
		time.sleep(10)
		try:
			del self.session[session.id]
		except:
			pass
		return self.response.false()
	def connect(self, data, connection):
		""" request connect to other machine """
		print data
		try:
			token 	 	= data["token"]
			id_machine 	= data["id_machine"]
			destination	= data["destination"]
			workgroup_id = data["workgroup_id"]
			workgroup_secret = data["workgroup_secret"]
			host 	= None
			mac 	= None
			if self._check_ismac(destination):
				mac = destination
			else:
				host = destination
		except:
			return response.false()
		if token and self.check_token(token):
			try:
				access = AccessToken.objects.get(token=token)
			except AccessToken.DoesNotExist:
				return self.response.false()

			machine = self.get_machine_domain(host, mac, access.user)
		elif workgroup_id:
			try:
				workgroup = Workgroup.objects.get(id=workgroup_id, secret_key=workgroup_secret)
			except Workgroup.DoesNotExist:
				return self.response.false()

			machine = self.get_machine_workgroup(host, mac, workgroup)
		else:
			return self.response.false()

		if machine.count() == 1:
			return self._connect_process(machine, data, connection)
		else:
			return self.response.connect(machine)
		return self.response.false()

	def connect_response(self, nata, natb, nata_tcp, natb_tcp):
		""" response type of connect """
		DIRECT 	= "DRT"		#for a: connect direct when b on the internet
		REVERS 	= "REV" 	#for b: connect direct when a on the internet
		THOLE	= "THO"		#for a, b: connect via tcp hole punching, a and b is cone nat
		MHOLE	= "MHO"		#for a, b: connect via tcp multi hole punching with ascending port
		MHOLED	= "MHD"		#for a, b: connect via tcp multi hole punching with deascending port
		UHOLE	= "UHO"		#for a, b: connect via udp hole punching
		RELAY 	= "REL"		#for a, b: connect use relay server, with symmetric nat

		# connect table of different nat RFC 3489
		#----------------------------------------------------------------------------------
		# NATA/NATB	| Drect | Full cone | Restricted Cone 	| Port Restricted 	| symmetric
		# Direct 	| dir 	| reversal 	| reversal	 		| reversal			| reversal
		# Full cone | dir 	| direct	| reversal	 		| reversal			| reversal
		# R Cone 	| dir 	| direct 	| udp hole 			| udp hole			| udp hole
		# P R Cone	| dir 	| direct 	| udp hole			| udp hole			| relay
		# Symmetric	| dir 	| direct 	| udp hole 			| relay				| relay
		# --------------------------------------------------------------------------------
		# if connect not work, it will connect via udp hole --> relay
		# nat type 1 - 12 view RFC 5389, RFC 5780
		# nat tcp type 1-5 and 10
		# connect table of different nat RFC 5780
		# NATA/NATB | 

		# return if internet or full cone nat
		if natb == 1 or natb == 10:
			return DIRECT
		if nata == 1 or nata == 10:
			return REVERS
		if nata_tcp == 10 and nata in [11, 12]:
			if natb in range(1, 4):
				return THOLE
		if natb_tcp == 10 and natb in [11, 12]:
			if nata in range(1, 4):
				return THOLE
		# connect via TCP
		if nata_tcp == 1 and natb_tcp == 1:
			if nata in range(1, 4) and natb in range(1,4):
				return THOLE
		if (nata_tcp == 4 and natb_tcp == 1 ) or (nata_tcp == 1 and natb_tcp == 4 ):
			if nata in range(1, 4) and natb in range(1,4):
				return MHOLE
		if (nata_tcp == 5 and natb_tcp == 1 ) or (nata_tcp == 1 and natb_tcp == 5 ):
			if nata in range(1, 4) and natb in range(1,4):
				return MHOLED

		# connect via UDP
		if nata in [1,2,3,4,7,10,11,12] or natb in [1,2,3,4,7,10,11,12]:
			return UHOLE
		return RELAY

	def accept_connect(self, data, connection):
		ERROR = False
		try:
			session_id = data["session"]
			id_machine = data["id_machine"]
			laddr 	= data["laddr"]
			lport 	= data["lport"]
			mac_accept = data["mac_accept"]
		except:
			ERROR == True
		try:
			session = Session.objects.get(id=str(session_id))
		except:
			ERROR = True
		try:
			machine = Machine.objects.get(id=str(id_machine))
		except:
			ERROR = True

		if not mac_accept or ERROR:
			connp.send_obj(self.response.false())
			connection.send_obj(self.response.false())
			connp.close()
			connection.close()
			del self.session[session_id]
			return False

		print "linked request session: %s" % session_id
		nata = session.nat
		nata_tcp = session.nat_tcp
		natb = machine.nat
		natb_tcp = machine.nat_tcp

		work = self.connect_response(nata, natb, nata_tcp, natb_tcp)
		connp = self.session[session_id]
		addr, port = connection.getpeername()
		p = self.response.accept_connect(session_id, laddr,
		 	lport, addr, port, session.addr, work, session.dest_port)
		q = self.response.accept_connect(session_id, session.laddr,
			session.lport, session.addr, session.port, addr, work, session.dest_port)
		connp.send_obj(p)
		connection.send_obj(q)
		connp.close()
		connection.close()
		del self.session[session_id]
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
			conna.settimeout(None)
			connb.settimeout(None)
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
			addr = udp.addr
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
					session.udphost = host
					session.udpport = port
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