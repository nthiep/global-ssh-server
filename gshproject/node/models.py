from django.db import models
from django.db.models.signals import post_save
from node.utils import create_gateway
from manage.models import Domain, Workgroup

# Create your models here.
class Gateway(models.Model):	
	ip  	= models.CharField(max_length=256)
	city  	= models.CharField(max_length=256)
	country  = models.CharField(max_length=256)
	def __str__(self):
		return self.ip
class Machine(models.Model):
	gateway	= models.ForeignKey(Gateway, null=True, blank=True)
	domain 	= models.ForeignKey(Domain, null=True, blank=True)
	workgroup = models.ForeignKey(Workgroup, null=True, blank=True)
	added 	= models.DateTimeField(auto_now_add=True, auto_now=True)
	mac  	= models.CharField(max_length=256)
	hostname = models.CharField(max_length=256)
	platform = models.CharField(max_length=256)
	ip   	= models.CharField(max_length=256)
	private = models.BooleanField(default=False)
	nat 	= models.IntegerField(default=9)
	nat_tcp = models.IntegerField(default=3)
	def __str__(self):
		return str(self.mac)

post_save.connect(create_gateway, sender=Gateway)