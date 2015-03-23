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
class Handle(Thread):

	def __init__(self, connection, mac, listpeer, machine, apinet):
		super(Handle, self).__init__()
		self.daemon 	= True
		self.connection = connection
		self.mac 		= mac
		self.listpeer 	= listpeer
		self.machine 	= machine
		self.apinet 	= apinet
	def remove_peer(self):
		""" remove all infomation of machine when disconnect """

		self.listpeer.remove(self.mac)
		self.machine.removemac(self.mac)
		self.apinet.removemac(self.mac)
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