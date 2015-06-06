Global-SSH-Server
==========
Description: Global-SSH socket server is help client connect.
			Webservice manager user, domain, machine.

<!-- highlight:-d language:console -->
	Author: Nguyen Thanh Hiep and Nguyen Huu Dinh
	Platform: Django, Django-rest-framework
	Database: MongoDB
How use it:
-------
Use virtual environment:
----
<!-- highlight:-d language:console -->
	$ [sudo] pip install virtualenv
clone source code:
<!-- highlight:-d language:console -->
	$ git clone https://github.com/nthiep/global-ssh-server.git
	$   
create environment:
<!-- highlight:-d language:console -->
	$ virtualenv global-ssh-server
	$ source  global-ssh-server/bin/activate
run server:
<!-- highlight:-d language:console -->
	$ python global-ssh-server/gshproject/manager.py runserver
Use Apache Server:
----
edit in /etc/apache2/sites-enabled/000-default.conf

<!-- highlight:-d language:console -->
	Alias /static /root/global-ssh-server/gshproject/static
    	<Directory /root/global-ssh-server/gshproject/static>
        	Require all granted
   	</Directory>

    	<Directory /root/global-ssh-server/gshproject/gshproject>
        	<Files wsgi.py>
           	 Require all granted
        	</Files>
    	</Directory>

    WSGIDaemonProcess gshproject python-path=/root/global-ssh-server:/root/global-ssh-server/lib/python2.7/site-packages
	WSGIProcessGroup gshproject
	WSGIScriptAlias / /root/global-ssh-server/gshproject/gshproject/wsgi.py
	SetEnv DJANGO_SETTINGS_MODULE gshproject.settings
	WSGIPassAuthorization On
restart Apache
<!-- highlight:-d language:console -->
	$ service apache2 restart
enable ssl in /etc/apache2/sites-enabled/default-ssl.conf
<!-- highlight:-d language:console -->
	SSLCertificateFile	/etc/apache2/ssl/apache.crt
	SSLCertificateKeyFile /etc/apache2/ssl/apache.key
 
View details at: https://gssh.github.io
-------