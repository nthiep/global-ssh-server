#!/usr/bin/env python
#
# Name:			network module
# Description:	network object
#

from bson.objectid import ObjectId
class Networks(object):
	"""this is class Networks, use to view other machine"""
	def __init__(self, data, datatype):
		self.data = data
		self.database = datatype
	def getnetname(self, netid):
		"""
		get network name
		"""
		return getattr(self, "_%s_getnetname" %self.database)(netid)
	def checkadmin(self, mac, netid):
		""" check admin machine """

		return getattr(self, "_%s_checkadmin" %self.database)(mac, netid)
	
	def addnetwork(self, mac, netname, apikey):
		"""
		add network to database
		"""
		return getattr(self, "_%s_addnetwork" %self.database)(mac, netname, apikey)
	def checknetwork(self, netid, apikey):
		""" check network is right """
		return getattr(self, "_%s_checknetwork" %self.database)(netid, apikey)
	def removenet(self, netid):
		""" remove network """
		return getattr(self, "_%s_removenet" %self.database)(netid)
	
	def _mongo_removenet(self, netid):
		""" remove network mongodb """
		self.data.networks.remove({"_id": ObjectId(netid)})

	def _mongo_checkadmin(self, mac, netid):
		""" check machine is admin """
		if self.data.networks.find_one({"_id": ObjectId(netid), "admin": mac}):
			return True
		return False
	def _mongo_getnetname(self, netid):
		"""
		get network from mongo Database
		"""
		return self.data.networks.find_one({"_id": ObjectId(netid)})
	def _mongo_checknetwork(self, netid, apikey):
		""" check network """
		if self.data.networks.find_one({"_id": ObjectId(netid), "apikey": apikey}):
			return True
		return False
	def _mongo_addnetwork(self, mac, netname, apikey):
		"""
		add network to mongo Database
		"""
		obj = {"netname": netname, "apikey": apikey, "admin": mac}
		_id = self.data.networks.insert(obj)
		return str(_id)

	def _mysql_getnetwork(self, netname):
		"""
		get network from mysql query
		"""
		pass
