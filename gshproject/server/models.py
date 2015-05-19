from django.db import models
# Create your models here.
class Session(models.Model):
	laddr 	= models.CharField(max_length=256)
	lport 	= models.IntegerField(default=0)
	addr 	= models.CharField(max_length=256)
	port 	= models.IntegerField(default=0)
	nat 	= models.IntegerField(default=0)
	nat_tcp = models.IntegerField(default=0)
	sport 	= models.IntegerField(default=0)
	udp 	= models.BooleanField(default=False)
	udphost = models.CharField(max_length=256)
	udpport = models.IntegerField(default=0)
	def __str__(self):
		return str(self.id)