from django.db import models
# Create your models here.
class Session(models.Model):
	added 	= models.DateTimeField(auto_now_add=True, auto_now=True)
	laddr 	= models.CharField(max_length=256, default="")
	lport 	= models.IntegerField(default=0)
	addr 	= models.CharField(max_length=256, default="")
	port 	= models.IntegerField(default=0)
	nat 	= models.IntegerField(default=0)
	nat_tcp = models.IntegerField(default=0)
	dest_port= models.IntegerField(default=0)
	def __str__(self):
		return str(self.id)
class UDPSession(models.Model):
	added 	= models.DateTimeField(auto_now_add=True, auto_now=True)
	session = models.ForeignKey(Session)
	addr 	= models.CharField(max_length=256, default="")
	port 	= models.IntegerField(default=0)
	def __str__(self):
		return str(self.id)
class RelaySession(models.Model):
	added 	= models.DateTimeField(auto_now_add=True, auto_now=True)
	session = models.ForeignKey(Session)
	sock_a 	= models.CharField(max_length=256, default="")
	sock_b 	= models.CharField(max_length=256, default="")
	def __str__(self):
		return str(self.id)