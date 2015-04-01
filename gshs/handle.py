#!/usr/bin/python
#
# Name:     Global SSH socket handle
# Description:  help connect ssh between client via return public ip and ramdom port.
#               use socket.
# project 2
# Server:   amazon server
#
# Author:   Nguyen Thanh Hiep - Nguyen Huu Dinh
# Time:     2015/03
# Requirements:  requirements.txt
#

from threading import Thread
import datetime, hashlib, json, time
from gshs 	import Database
from gshs 	import Machines
from gshs 	import APIusers
from gshs  	import APInets
class Handle(Thread):

	def __init__(self, connection, mac, listpeer):
		super(Handle, self).__init__()
		self.daemon 	= True
		self.connection = connection
		self.connection.set_timeout()
		self.mac 		= mac
		self.listpeer 	= listpeer
	def remove_peer(self):
		""" remove all infomation of machine when disconnect """
		try:
			conn = Database()
			database = conn.connect()
			datatype = conn.database
		except Exception, e:
			print e
			raise Exception("Database Error: can connect to database")

		machine 	= Machines(database, datatype)
		apiuser 	= APIusers(database, datatype)
		apinet 		= APInets(database, datatype)
		self.listpeer.remove(self.mac)
		machine.removemac(self.mac)
		apiuser.removemac(self.mac)
		apinet.removemac(self.mac)
	def run(self):
		while True:
			try:
				data = self.connection.read_obj()
				if data["request"] == "ping":
					self.connection.set_timeout()
				else:
					break
			except Exception,e:
				print str(e)
				break
		self.remove_peer()
		self.connection.close()