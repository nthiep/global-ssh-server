Global-SSH-Server-Webservice

==========

Description: Global-SSH server is help client connect.
			Webservice manager user, domain, machine.

Author: Nguyen Thanh Hiep and Nguyen Huu Dinh
Platform: Django
Database: MongoDB
How use it:
-------
you need virtual environment to run:
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
	$ cd global-ssh-server/gshproject
	$ python manager.py runserver
you can edit database in global-ssh-server/gshproject/gshproject/seting.py
View details at: https://gssh.github.io