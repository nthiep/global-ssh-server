#!/usr/bin/env python
#
# Name:			user module
# Description:	user object
#

class Users(object):
	def __init__(self, data, datatype):
		self.data = data
		self.database = datatype
	def getuser(self, username):
		"""
		get username
		"""
		return getattr(self, "_%s_getuser" %self.database)(username)

	def adduser(self, username, password, fullname, email, website):
		"""
		add user to database
		"""
		return self._mongo_adduser(username, password, fullname, email, website)

	def checkauth(self, username, password):
		""" check request login """
		try:
			if self.data.users.find_one({"username": username, "password": password}) is not None:
				return True
		except:
			pass
		return False

	def _mongo_getuser(self, username):
		"""
		get username for mongo Database
		"""
		if not self._mongo_checkuser(username):
			return self.data.users.find_one({"username": username})
		return False
	def _mongo_checkuser(self, username):
		"""
		get username for mongo Database
		"""
		if self.data.users.find_one({ 'username':  username}):
			return True
		return False

	def _mongo_adduser(self, username, password, fullname, email, website):
		"""
		add username for mongo Database
		"""
		if not self._mongo_checkuser(username):
			self.data.users.insert({'username': username, 'password': password, 'fullname': fullname, 'email': email, 'website': website})
			return True
		return False

	def _mysql_getuser(self, username):
		"""
		get username for mysql query
		"""
		pass
