#!/usr/bin/env python
import os, sys
from distutils.core import setup
_locals = {}
with open('gsh/_version.py') as fp:
    exec(fp.read(), None, _locals)
version = _locals['__version__']
setup(name        ='gshs',
      version     =version,
      description ='global ssh server',
      long_description=open('README.md').read(),
      author      ='Hiep Thanh',
      author_email='hieptux@gmail.com',
      url         ='https://github.com/nthiep/global-ssh-server',      
      packages    =['gshs'],
      license     = 'GNU',
      scripts     =['bin/gshs', 'bin/gshsd'],
      data_files  =[('/etc/init.d', ['etc/init.d/gshsd']),
                  ('/etc/gshs', ['etc/gshs/gshs.conf'])]
     )

if sys.argv[1] == 'install':
      print "chmod for gshs ..."
      os.system("chmod +x /etc/init.d/gshsd")
      print "chmod success.----ok"
      print "chmod for gshs.conf ..."
      os.system("chmod +r /etc/gshs/gshs.conf")
      print "chmod success.----ok"
"""
      print "create run level rc.d ..."
      for x in range(2,5):
            os.system("ln -s /etc/init.d/gshsd /etc/rc%d.d/S99gshsd" %x)
      for x in [0,1,6]:
            os.system("ln -s /etc/init.d/gshsd /etc/rc%d.d/K20gshsd" %x)
      print "create success.----ok"
"""