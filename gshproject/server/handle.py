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
from node.models import Machine
class Handle(Thread):

	def __init__(self, connection, mac, listpeer):
		super(Handle, self).__init__()
		self.daemon 	= True
		self.connection = connection
		self.mac 		= mac
		self.listpeer 	= listpeer
	def remove_peer(self):
		""" remove all infomation of machine when disconnect """
		machine = Machine.objects.get(mac=self.mac)
		machine.delete()
		self.listpeer.remove(self.mac)
	def run(self):
		while True:
			try:
				data = self.connection.read_obj()
			except Exception,e:
				print str(e)
				break
		self.remove_peer()
		self.connection.close()