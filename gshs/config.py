#!/usr/bin/env python
#
# Name:			Configuration file
# Description:	Configuration file
#

from ConfigParser import ConfigParser
# change config file if you move to another place 
CONFIG_FILE = "/etc/gshs/gshs.conf"

# Configuration variable
parser = ConfigParser()
parser.read(CONFIG_FILE)

# option value

DATA_SECTION = 'DataBase'

# seting if use mongobd
URL_MONGO  = 'UrlMongo'
HOST_MONGO = 'HostMongo'
PORT_MONGO = 'PortMongo'

# seting if use mysql database
HOST_MYSQL = 'HostMysql'
USER_MYSQL = 'UserMysql'
PASS_MYSQL = 'PassMysql'

# database name

DATA_NAME = 'DataName'


# ssh server config
SV_SECTION  = 'Server'
SV_PORT 	= 'Port'
SV_TIME		= 'Timeout'

SERVER_PORT 	= int(parser.get(SV_SECTION, SV_PORT))
SERVER_TIMEOUT 	= int(parser.get(SV_SECTION, SV_TIME))

LOG_FILENAME 	= "/var/log/gshs.log"