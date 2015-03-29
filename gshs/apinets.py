#!/usr/bin/env python
#
# Name:			APIkey of network module
# Description:	apikey network object
#

class APInets(object):
	"""
	apikey for machine of network
	"""
	def __init__(self, data, datatype):
		self.data = data
		self.datatype = datatype

	def addapi(self, mac, netid):
		"""
		add key to database
		"""
		return getattr(self, "_%s_addapi" %self.datatype)(mac, netid)

	def listmac(self, mac):
		""" return all machine has same network with mac """

		lsnet =  getattr(self, "_%s_listnet" %self.datatype)(mac)
		return getattr(self, "_%s_listmac" %self.datatype)(lsnet)
	def removemac(self, mac):
		"""
		remove all network of machine
		"""
		return getattr(self, "_%s_removemac" %self.datatype)(mac)
	def renetmac(self, mac, netid):
		""" remove network of machine """
		return getattr(self, "_%s_renetmac" %self.datatype)(mac, netid)
	def removenet(self, netid):
		""" remove all machine of network """
		return getattr(self, "_%s_removenet" %self.datatype)(netid)
	def removeall(self):
		"""
		remove all
		"""
		return getattr(self, "_%s_removeall" %self.datatype)()
	def _mongo_renetmac(self, mac, netid):
		""" same remove network by mongo database """
		self.data.apinets.remove({"mac": mac, "netid": netid})	
	def _mongo_removenet(self, netid):
		""" remove all machine of network by mongo database """
		self.data.apinets.remove({"netid": netid})	
	
	def _mongo_checkapi(self, mac, netid):
		"""
		check api key of network for mongo Database
		"""
		if self.data.apinets.find_one({ "mac" : mac, "netid": netid }):
			return True
		return False

	def _mongo_addapi(self, mac, netid):
		"""
		add api key to mongo Database
		"""
		if not self._mongo_checkapi(mac, netid):
			self.data.apinets.insert({"mac": mac, "netid": netid})
		return True

	def _mongo_listnet(self, mac):
		""" return all network of machine """
		ls = self.data.apinets.find({"mac": mac}, {"netid": 1})
		rs = []
		for l in ls:
			rs.append(l["netid"])
		return rs
	def _mongo_listmac(self, lsnet):
		""" return all machines in network list """
		ls = self.data.apinets.find({"netid": {"$in": lsnet}}, {"mac": 1})
		rs = []
		for l in ls:
			rs.append(l["mac"])
		return rs
	def _mongo_removemac(self, mac):
		""" remove all network of machine """
		self.data.apinets.remove({"mac": mac})
	def _mongo_removeall(self):
		""" remove all """
		self.data.apinets.remove({})