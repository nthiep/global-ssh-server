from django.db import models
# Create your models here.
class Session(models.Model):
	laddr = models.CharField(max_length=256)
	lport = models.CharField(max_length=256)
	addr = models.CharField(max_length=256)
	port = models.CharField(max_length=256)
	nat = models.CharField(max_length=256)
	issym = models.CharField(max_length=256)
	sport = models.CharField(max_length=256)
	udp = models.BooleanField(default=False)
	udphost = models.CharField(max_length=256)
	udpport = models.CharField(max_length=256)
	def __str__(self):
		return str(self.id)