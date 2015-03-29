#!/usr/bin/env python
#
# Name:			sessions module
# Description:	sessions object
#
import sys, datetime
class Sessions(object):
	"""this is class sessions, use for request connection """
	def __init__(self, data, datatype):
		self.data = data
		self.datatype = datatype
	def getsession(self, session):
		"""
		get session
		"""
		return getattr(self, "_%s_getsession" %self.datatype)(session)

	def addsession(self, session, laddr, lport, addr, port, nat):
		"""
		add session to database
		"""
		return getattr(self, "_%s_addsession" %self.datatype)(session, laddr, lport, addr, port, nat)
	def addudpsession(self, session, addr, port):
		"""
		add udp session to database
		"""
		return getattr(self, "_%s_addudpsession" %self.datatype)(session, addr, port)

	def getudpsession(self, session):
		"""
		check session
		"""
		return getattr(self, "_%s_getudpsession" %self.datatype)(session)

	def checksession(self, session):
		"""
		check session
		"""
		return getattr(self, "_%s_checksession" %self.datatype)(session)
	def _mongo_getsession(self, session):
		"""
		get session for mongo Database
		"""
		return self.data.sessions.find_one({"session": session})

	def _mongo_checksession(self, session):
		"""
		check session is exists
		"""
		if self.data.sessions.find_one({ "session" : session }):
			return True
		return False

	def _mongo_addsession(self, session, laddr, lport, addr, port, nat):
		"""
		add session to mongo Database
		"""
		timestamp = datetime.datetime.now()
		utc_timestamp = datetime.datetime.utcnow()
		self.data.sessions.ensure_index("time",expireAfterSeconds = 10)
		self.data.sessions.insert({"time": utc_timestamp, "session": session,
					 "laddr": laddr, "lport": lport, "addr": addr, "port": port, "nat": nat})
		return True

	def _mongo_getudpsession(self, session):
		"""
		check udp session is exists
		"""
		data = self.data.sessions.find_one({ "udpsession" : session })
		if data:
			return data
		return False
	def _mongo_addudpsession(self, session, addr, port):
		"""
		add udp session to mongo Database
		"""
		timestamp = datetime.datetime.now()
		utc_timestamp = datetime.datetime.utcnow()
		self.data.sessions.ensure_index("time",expireAfterSeconds = 10)
		self.data.sessions.insert({"time": utc_timestamp,
				 "udpsession": session, "addr": addr, "port": port})
		return True
