#!/usr/bin/env python
#
# Name:			APIkey of username module
# Description:	apikey object
#

class APIusers(object):
	"""
	apikey for machine of user
	"""
	def __init__(self, data, datatype):
		self.data = data
		self.datatype = datatype

	def getuser(self, key):
		"""
		get username
		"""
		return getattr(self, "_%s_getuser" %self.datatype)(key)

	def addapikey(self, username, mac, key):
		"""
		add key to database
		"""
		return getattr(self, "_%s_addapi" %self.datatype)(username, mac, key)

	def checkapi(self, mac, key):
		return getattr(self, "_%s_checkapi" %self.datatype)(mac, key)

	def listmac(self, username):
		""" return all machine of username """
		return getattr(self, "_%s_listmac" %self.datatype)(username)
		
	def _mongo_listmac(self, username):
		""" output all list machine of username """
		ls = self.data.apiusers.find({"username": username}, {"mac": 1})
		rs = []
		for l in ls:
			rs.append(l["mac"])
		return rs

	def _mongo_getuser(self, key):
		"""
		get username for mongo Database
		"""
		data = self.data.apiusers.find_one({"key": key})
		return data["username"]

	def _mongo_checkapi(self, mac, key):
		"""
		check api key for mongo Database
		"""
		if self.data.apiusers.find({ "mac" : mac, "key": key }):
			return True
		return False
	def _mongo_checkmac(self, mac):
		"""check mac in api"""
		if self.data.apiusers.find_one({ "mac" : mac}):
			return True
		return False
	def _mongo_addapi(self, username, mac, key):
		"""
		add api key to mongo Database
		"""
		if self._mongo_checkmac(mac):
			self.data.apiusers.update({"mac" : mac}, {"$set": {"username": username, "key": key}})
		else:
			self.data.apiusers.insert({"username": username, "mac": mac, "key": key})
		return True

