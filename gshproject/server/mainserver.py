#!/usr/bin/python
#
# Name:     Global SSH socket server
# Description:  help connect ssh between client via return public ip and ramdom port.
#               use socket.
# project 2
# Server:   amazon server
#
# Author:   Nguyen Thanh Hiep - Nguyen Huu Dinh
# Time:     2015/03
# Requirements:  requirements.txt
#

import sys, socket, json, random, hashlib, struct, thread
from threading import Thread
import logging.handlers, logging
from .request import Request
from .jsocket import JsonSocket
from .config import SERVER_PORT, SERVER_TIMEOUT, LOG_FILENAME

LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"


# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
	def __init__(self, logger, level):
		"""Needs a logger and a logger level."""
		self.logger = logger
		self.level = level
 
	def write(self, message):
		# Only log if there is a message (not just a new line)
		if message.rstrip() != "":
			self.logger.log(self.level, message.rstrip())
 
class SocketServer(Thread):
	def __init__(self):
		super(SocketServer, self).__init__()
		self.daemon 	= True
		self.request	= Request()
		self.sock 	= JsonSocket(JsonSocket.TCP)
		self.sock.set_server()
	def process(self, connection):
		conn 	= JsonSocket(JsonSocket.TCP)
		conn.set_socket(connection)
		conn.set_timeout()
		data	= conn.read_obj()
		question	= self.request.get_request(data)
		print "%s with request %s" %(str(conn.getpeername()), question)
		response 	= getattr(self.request, question)(data, conn)
		if response:
			conn.send_obj(response)
			conn.close()
		return
	def run(self):
		print "server is running..."
		while True:
			connection 	= self.sock.accept_connection()
			thread.start_new_thread(self.process, (connection,))