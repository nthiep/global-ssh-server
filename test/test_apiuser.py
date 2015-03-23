"""
this is test module for class in gshs
"""

import unittest
import os, sys, json
lib_path = os.path.abspath(os.path.join('..', ''))
sys.path.append(lib_path)
from gshs import APIusers
from gshs import Database
class Test_Request(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super(Test_Request, self).__init__(*args, **kwargs)
		
	def setUp(self):
		conn = Database()
		self.data = conn.connect()
		self.api = APIusers(self.data, self.data.database)

	def test_listmac(self):
		# test list mac
		
		self.assertTrue(self.checkEqual(["94:db:c9:41:85:5d"], self.api.listmac("hiep")))
	def checkEqual(self,L1, L2):
		print L2
		if sorted(L1) == sorted(L2):
			print "the two lists are the same"
			return True
		else:
			print "the two lists are not the same"
			return False

if __name__ == '__main__':
    unittest.main()