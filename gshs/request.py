#!/usr/bin/env python
#
# Name:			request module
# Description:	request class object
#

import json, hashlib, random, time
from gshs 	import Users
from gshs 	import Machines
from gshs 	import APIusers
from gshs 	import Database
from gshs  	import APInets
from gshs 	import Networks
from gshs  	import Handle
from gshs	import Response
from gshs	import Sessions
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
		except:
			raise Exception("Database Error: can connect to database")
		self.listpeer = ls_connect()
		self.session  = {}
		self.response = Response()
	def get_request(self, data):
		"""
		return to request type of user
		"""
		keep  = False
		close = False
		if data["request"] in ['authentication', 'authnetwork', 'connect', 'accept_connect']:
			keep = True
			if data["request"] in [ 'accept_connect', 'connect']:
				close = True
		return data["request"], keep, close


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
			token = self.createtoken()
			api = APIusers(self.database, self.datatype)	
			api.addapikey(username, mac, token)
			return token
		return False

	def register(self, data):
		"""
		request login of client
		"""
		username = data["username"]
		passwork = data["passwork"]
		fullname = data["fullname"]
		email	 = data["email"]
		website	 = data["website"]
		user = Users(self.database, self.datatype)
		pswd = hashlib.sha1(passwork).hexdigest()
		return user.adduser(username, pswd, fullname, email, website)

	def _add_peer(self, mac, connection, hostname, platform):
		""" add peer handle if not exist"""
		machine 	= Machines(self.database, self.datatype)
		apinet 		= APInets(self.database, self.datatype)
		if not machine.checkmachine(mac):
			machine.addmachine(mac, hostname, platform)
		if not self.listpeer.check(mac):
			peer 		= peer_mac(mac, connection)
			self.listpeer.addpeer(peer)
			newhandle 	= Handle(connection, mac, self.listpeer, machine, apinet)
			newhandle.start()
	def authentication(self, data, connection):
		""" authentication of api key user """
		apikey  	 = data["api"]
		mac 	 = data["mac"]
		hostname = data["hostname"]
		platform = data["platform"]
		api 	 = APIusers(self.database, self.datatype)
		if api.checkapi(mac, apikey):
			self._add_peer(mac, connection, hostname, platform)
			return True
		return False

	def authnetwork(self, data, connection):
		""" request of add network """
		netkey  = data["netkey"]
		mac 	= data["mac"]
		hostname = data["hostname"]
		platform = data["platform"]
		nw 		= Networks(self.database, self.datatype)
		i = 0
		for k in netkey:
			if nw.checknetwork(k[:24], k[24:]):
				api = APInets(self.database, self.datatype)
				if api.addapi(mac, k[:24]):
					i += 1
		if i != 0:
			self._add_peer(mac, connection, hostname, platform)	
		return str(i) + '/' + str(len(netkey))

	def createnetwork(self, data):
		""" add network """
		mac 	= data["mac"]
		netname = data["netname"]
		netkey  = self.createtoken()
		nw 		= Networks(self.database, self.datatype)
		netid = nw.addnetwork(mac, netname, netkey)
		return netid + netkey

	def listmachine(self, data):
		""" response all machine of client """
		mac  = data["mac"]
		key	 = data["key"]

		apiu = APIusers(self.database, self.datatype)
		apin = APInets(self.database, self.datatype)
		m 	 = Machines(self.database, self.datatype)	
		au   = apiu.getuser(key)
		lsmu = apiu.listmac(au)
		lsmn = apin.listmac(mac)
		mu = False
		mn = False
		if len(lsmu) != 0:
			mu   = list(m.listmachine(lsmu))
		if len(lsmn) != 0:
			mn 	 = list(m.listmachine(lsmn))
		return self.response.listmachine(mu, mn)

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

	def _connect_process(self, peermac, data, connection):
		ss = self.createtoken()
		ses 	= Sessions(self.database, self.datatype)
		self.session[ss] = connection
		addr, port = connection.getpeername()
		ses.addsession(ss, data["laddr"], data["lport"], addr, port)
		connp = self.listpeer.getconnect(peermac)
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
		key  	 = data["key"]
		mac 	 = data["mac"]
		peer	 = data["peer"]
		nw 		 = Networks(self.database, self.datatype)
		apiu 	 = APIusers(self.database, self.datatype)
		apin 	 = APInets(self.database, self.datatype)
		m 		 = Machines(self.database, self.datatype)
		au   	 = apiu.getuser(key)
		lsmu 	 = apiu.listmac(au)
		lsmn 	 = apin.listmac(mac)
		lsm = lsmu + lsmn
		if len(lsm) !=0:
			ls   = list(m.listhost(lsmu, peer))
			if len(ls) == 1:
				self._connect_process(ls[0]["mac"], data, connection)
			elif len(ls) > 1:
				return ls
		return False

	def accept_connect(self, data, connection):
		ses 	= Sessions(self.database, self.datatype)
		if ses.checksession(data["session"]):
			print "linked request session: %s" % data["session"]
			peer = ses.getsession(data["session"])
			connp = self.session[data["session"]]
			addr, port = connection.getpeername()
			p = {"session": data["session"], "lport" : data["lport"], "laddr": data["laddr"], "port": port,
			 "addr": addr, "me": peer["addr"]}
			q = {"lport" : peer["lport"], "laddr": peer["laddr"], "port": peer["port"],
			 "addr": peer["addr"], "me" :addr}
			connp.send_obj(p)
			connp.close()
			del self.session[data["session"]]
			return q
		return False


				

