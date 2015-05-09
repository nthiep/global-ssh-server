from django.db import models
from manage.models import Domain, Workgroup

# Create your models here.
class Gateway(models.Model):	
	ip  = models.CharField(max_length=256)
	nat = models.CharField(max_length=256)
	sym = models.BooleanField(default=False)
	def __str__(self):
		return self.ip
class Machine(models.Model):
	gateway	 = models.ForeignKey(Gateway, null=True, blank=True)
	domain 	 = models.ForeignKey(Domain, null=True, blank=True)
	workgroup = models.ForeignKey(Workgroup, null=True, blank=True)
	added = models.DateTimeField(auto_now_add=True, auto_now=True)
	mac  = models.CharField(max_length=256)
	hostname = models.CharField(max_length=256)
	platform = models.CharField(max_length=256)
	ip   = models.CharField(max_length=256)
	private = models.BooleanField(default=False)
	def __str__(self):
		return str(self.mac)