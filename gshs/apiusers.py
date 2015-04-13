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

	def addapimac(self, username, mac):
		"""
		add machine to user
		"""
		return getattr(self, "_%s_addapimac" %self.datatype)(username, mac)

	def listmac(self, username):
		""" return all machine of username """
		return getattr(self, "_%s_listmac" %self.datatype)(username)
	def removemac(self, mac, username):
		"""
		remove machine of user
		"""
		return getattr(self, "_%s_removemac" %self.datatype)(mac, username)
	def _mongo_listmac(self, username):
		""" output all list machine of username """
		ls = self.data.apiusers.find({"username": username}, {"mac": 1})
		rs = []
		for l in ls:
			rs.append(l["mac"])
		return rs

	def _mongo_checkmac(self, mac):
		"""check mac in api"""
		if self.data.apiusers.find_one({ "mac" : mac}):
			return True
		return False
	def _mongo_addapimac(self, username, mac):
		"""
		add api key to mongo Database
		"""
		if self._mongo_checkmac(mac):
			self.data.apiusers.update({"mac" : mac}, {"$set": {"username": username}})
		else:
			self.data.apiusers.insert({"mac": mac, "username": username})
		return True
	def _mongo_removemac(self, mac, username):
		""" remove machine of user """
		self.data.apiusers.remove({"mac": mac, "username": username})
