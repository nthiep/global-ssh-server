#!/usr/bin/env python
import os
from distutils.core import setup

setup(name='gshs',
      version='1.0.0',
      description='global ssh server',
      author='hiep',
      author_email='hieptux@gmail.com',
      url='https://www.python.org/',      
      packages=['gshs'],
      scripts=['bin/gshs'],
      data_files=[('/etc/init.d', ['bin/gshsd']),
                  ('/etc/gshs', ['gshs/gshs.conf'])]
     )
print "chmod for gshs..."
os.system("chmod +x /etc/init.d/gshsd")
print "chmod ok."