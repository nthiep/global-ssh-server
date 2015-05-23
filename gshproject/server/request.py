#!/usr/bin/env python
#
# Name:			request module
# Description:	request class object
#

import socket, json, hashlib, random, time, thread, re
from bson	import json_util

from django.utils import timezone
from node.models import Machine, Gateway
from oauth2_provider.models import AccessToken
from manage.models import Domain, Workgroup
from .handle import Handle
from .jsocket import JsonSocket
from .response import Response
from .models import Session, UDPSession, RelaySession

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
		self.relay_sock  	= {}
		self.udp_hole_sock 	= {}
		self.response = Response()
	def get_request(self, data):
		"""
		return to request type of user
		"""
		return data["request"]

	def keepconnect(self, data, connection):
		try:
			mac 	 = data["mac"]
			hostname = data["hostname"]
			platform = data["platform"]
			ip 		 = data["ip"]
			private  = data["private"]
		except:
			return self.response.false("Request Not Accept")

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
		return self.response.false("Machine Already Online")
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
			if mac:
				return Machine.objects.filter(mac=mac, domain=domain, private=False)
			elif host:
				return Machine.objects.filter(hostname=host, domain=domain, private=False)
			return False
		except Machine.DoesNotExist:
			print "not machine in domain"
			return False
	def get_machine_workgroup(self, host=None, mac=None, workgroup=None):
		try:
			if mac:
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
			return self.response.false("Machine Not Online")
		nat = source.nat
		nat_tcp = source.nat_tcp
		session, created 	= Session.objects.get_or_create(laddr=data["laddr"], lport=data["lport"], 
			addr = addr, port = port, nat = nat, nat_tcp=nat_tcp, dest_port = data["destination_port"])
		self.session[session.id] = connection
		connp = self.listpeer.getconnect(machine[0].mac)
		if not connp:
			return self.response.false("Peer Not Online")
		connp.send_obj(self.response.request_connect(session.id, source.mac))
		time.sleep(10)
		try:
			del self.session[session.id]
		except:
			pass
		return self.response.false("Peer Not Response")
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
			return self.response.false("Request Not Accept")
		if token and self.check_token(token):
			try:
				access = AccessToken.objects.get(token=token)
			except AccessToken.DoesNotExist:
				return self.response.false("AccessToken Not Accept")

			machine = self.get_machine_domain(host, mac, access.user)
		elif workgroup_id:
			try:
				workgroup = Workgroup.objects.get(id=workgroup_id, secret_key=workgroup_secret)
			except Workgroup.DoesNotExist:
				return self.response.false("Workgroup Not Accept")

			machine = self.get_machine_workgroup(host, mac, workgroup)
		else:
			return self.response.false("Machine Not Online")

		if machine.count() == 1:
			return self._connect_process(machine, data, connection)
		elif machine.count() > 1:
			return self.response.connect(machine)
		return self.response.false("Machine Not Online")

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
		mac_accept = True
		try:
			session_id = data["session"]
			id_machine = data["id_machine"]
			mac_accept = data["mac_accept"]
		except:
			ERROR = True
		try:
			session = Session.objects.get(id=str(session_id))
		except:
			ERROR = True
		try:
			machine = Machine.objects.get(id=str(id_machine))
		except:
			ERROR = True

		if not mac_accept or ERROR:
			connp = self.session[session_id]
			connp.send_obj(self.response.false("Machine Not Accept"))
			connection.send_obj(self.response.false("Not Accept Machine"))
			connp.close()
			connection.close()
			del self.session[session_id]
			return False

		print "linked request session: %s" % session_id
		laddr 	= data["laddr"]
		lport 	= data["lport"]		
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
			del self.relay_sock[session]
		except:
			pass
	def _check_udp_session(self, session):
		try:
			self.udp_hole_sock[session]
			return True
		except:
			pass
		return False 
	def _check_session(self, session):
		try:
			self.relay_sock[session]
			return True
		except:
			pass
		return False 
	def relay(self, data, connection):
		try:
			session_id = data["session"]		
		except:
			return self.response.false("Request not Accept")
		try:
			session = Session.objects.get(id=session_id)
		except:			
			return self.response.false("Session Not Accept")
		if self._check_session(session_id):
			print "Have Session %s" %session_id
			conna = connection.get_conn()
			connb = self.relay_sock[session_id]
			conna.settimeout(None)
			connb.settimeout(None)
			thread.start_new_thread(self._relay_forward, (session_id, conna, connb))			
			thread.start_new_thread(self._relay_forward, (session_id, connb, conna))
			relay_session, created = RelaySession.objects.get_or_create(session=session, \
						sock_a = "%s:%d"%conna.getpeername(), sock_b="%s:%d"%connb.getpeername)
			del self.relay_sock[session_id]
			print "Start Thread Relay %s" %session_id
		else:
			print "Add Session Relay %s" %session_id
			self.relay_sock[session_id] = connection.get_conn()
		return False
	def udp_hole(self, data, connection):
		try:
			session_id = data["session"]
		except:
			return self.response.false("Request not Accept")
		try:
			session = Session.objects.get(id=session_id)
		except:			
			return self.response.false("Session Not Accept")
		if self._check_udp_session(session_id):
			port = self.session[session_id]
			del self.udp_hole_sock[session_id]
			return self.response.udp_hole(port)
		else:
			udp = JsonSocket(JsonSocket.UDP)
			port = udp.set_server(0)
			self.udp_hole_sock[session_id] = port
			thread.start_new_thread(self.udp_connect, (session_id, udp))
			return self.response.udp_hole(port)

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
				except:
					continue
				try:
					udp_session = UDPSession.objects.get(session=session)
					udp.send_obj({"host": host, "port": port}, (udp_session.addr, int(udp_session.port)))
					udp.send_obj({"host": udp_session.addr, "port": udp_session.port}, addr)
					print "linked session %s" % session_id
					break
				except UDPSession.DoesNotExist:
					udp_session, created = UDPSession.objects.get_or_create(addr=host,\
											 port=port, session=session)
					continue					
			except:
				continue
		udp.close()