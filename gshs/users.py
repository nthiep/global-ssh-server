#!/usr/bin/env python
#
# Name:			user module
# Description:	user object
#

class Users(object):
	def __init__(self, data, datatype):
		self.data = data
		self.database = datatype
	def getuser(self, apikey):
		"""
		get username
		"""
		return getattr(self, "_%s_getuser" %self.database)(apikey)

	def adduser(self, username, password, fullname, email, website, apikey):
		"""
		add user to database
		"""
		return self._mongo_adduser(username, password, fullname, email, website, apikey)

	def checkauth(self, username, password):
		""" check request login """
		try:
			if self.data.users.find_one({"username": username, "password": password}) is not None:
				return True
		except:
			pass
		return False
	def checkapikey(self, apikey):

		return getattr(self, "_%s_checkapikey" %self.database)(apikey)
	def getapikey(self, username):
		return getattr(self, "_%s_getapikey" %self.database)(username)

	def _mongo_getuser(self, apikey):
		"""
		get username for mongo Database
		"""
		us = self.data.users.find_one({"apikey": apikey})
		if us:
			return us["username"]
		return False
	def _mongo_checkuser(self, username):
		"""
		get username for mongo Database
		"""
		if self.data.users.find_one({ 'username':  username}):
			return True
		return False

	def _mongo_adduser(self, username, password, fullname, email, website, apikey):
		"""
		add username for mongo Database
		"""
		if not self._mongo_checkuser(username):
			self.data.users.insert({'username': username, 'password': password,
				'fullname': fullname, 'email': email, 'website': website, 'apikey': apikey})
			return True
		return False

	def _mongo_checkapikey(self, apikey):
		""" check apikey """
		if self.data.users.find_one({'apikey': apikey}):
			return True
		return False

	def _mongo_getapikey(self, username):
		""" check apikey """
		us = self.data.users.find_one({'username': username})
		if us:
			return us["apikey"]
		return False