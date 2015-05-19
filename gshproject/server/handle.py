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

	def __init__(self, connection, machine, listpeer):
		super(Handle, self).__init__()
		self.daemon 	= True
		self.connection = connection
		self.machine	= machine
		self.listpeer 	= listpeer
	def remove_peer(self):
		""" remove all infomation of machine when disconnect """
		self.machine.delete()
		self.listpeer.remove(self.machine.mac)
	def run(self):
		while True:
			try:
				data = self.connection.read_obj()
			except Exception,e:
				print str(e)
				break
		self.remove_peer()
		self.connection.close()