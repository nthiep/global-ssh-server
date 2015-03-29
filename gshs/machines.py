#!/usr/bin/env python
#
# Name:			machine module
# Description:	machine object
#
import sys
class Machines(object):
	"""this is class Machines, use to view other machine"""
	def __init__(self, data, datatype):
		self.data = data
		self.datatype = datatype
	def getmachine(self, machine):
		"""
		get machine
		"""
		return getattr(self, "_%s_getmachine" %self.datatype)(machine)

	def addmachine(self, mac, hostname, platform):
		"""
		add machine to database
		"""
		return getattr(self, "_%s_addmachine" %self.datatype)(mac, hostname, platform)
	def checkmachine(self, mac):
		"""
		add machine to database
		"""
		return getattr(self, "_%s_checkmachine" %self.datatype)(mac)
	def listmachine(self, lsmac):
		"""
		return list machines are online
		"""
		return getattr(self, "_%s_listmachine" %self.datatype)(lsmac)

	def listhost(self, lsmac, host):
		""" return list machine with hostname """
		return getattr(self, "_%s_listhost" %self.datatype)(lsmac, host)
	
	def removemac(self, mac):
		"""
		remove machine
		"""
		getattr(self, "_%s_remove" %self.datatype)(mac)
	def removeall(self):
		"""
		remove all machine
		"""
		getattr(self, "_%s_removeall" %self.datatype)()

	def editnat(self, mac, nat):
		""" edit nat of machine  """
		getattr(self, "_%s_editnat" %self.datatype)(mac, nat)

	def _mongo_editnat(self, mac, nat):

		if self._mongo_checkmachine(mac):
			self.data.machines.update({"mac" : mac}, {"$set":{"nat": nat}})
			return True
		return False


	def _mongo_listhost(self, lsmac, host):
		"""
		return list hostname mongodb
		"""
		return self.data.machines.find({"mac": {"$in": lsmac}, "hostname": host}, {"_id": 0})
	def _mongo_getmachine(self, mac):
		"""
		get machine for mongo Database
		"""
		return self.data.machines.find_one({"mac": mac})

	def _mongo_checkmachine(self, mac):
		"""
		check machine is exists
		"""
		if self.data.machines.find_one({ "mac" : mac }):
			return True
		return False

	def _mongo_addmachine(self, mac, hostname, platform):
		"""
		add machine for mongo Database
		"""
		if self._mongo_checkmachine(mac):
			self.data.machines.update({"mac" : mac}, {"$set":{"hostname": hostname, "platform": platform}})
		else:
			self.data.machines.insert({"mac": mac, "hostname": hostname, "platform": platform})
		
		return True

	def _mongo_listmachine(self, lsmac):
		""" return list machines are online in list"""
		return self.data.machines.find({"mac": {"$in": lsmac}}, {"_id": 0})

	def _mongo_remove(self, mac):
		""" remove machine """
		self.data.machines.remove({"mac": mac})
	def _mongo_removeall(self):
		""" remove all machine """
		self.data.machines.remove({})