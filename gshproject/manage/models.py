from django.db import models
from django.contrib.auth.models import User, AbstractBaseUser
from oauth2_provider.models import AbstractApplication
from django.contrib.auth.hashers import check_password, make_password
# Create your models here.

class Domain(AbstractBaseUser):
	user   = models.ForeignKey(User)
	domain = models.CharField(max_length=256, unique=True)
	filter_mode = models.BooleanField(default=False)
	filter_type = models.BooleanField(default=False)
	listmac = models.TextField(null=True, blank=True)
	USERNAME_FIELD = 'domain'
	REQUIRED_FIELDS = []
	def set_password(self, raw_password):
		self.password = make_password(raw_password)

	def check_password(self, raw_password):
		"""
		Returns a boolean of whether the raw_password was correct. Handles
		hashing formats behind the scenes.
		"""
		def setter(raw_password):
			self.set_password(raw_password)
			self.save(update_fields=["password"])
		return check_password(raw_password, self.password, setter)
	def __str__(self):
		return self.domain

class Workgroup(models.Model):
	workgroup = models.CharField(max_length=256, null=True, blank=True)
	secret_key  = models.CharField(max_length=256)
	mac_admin = models.CharField(max_length=256)
	def __str__(self):
		return self.id
class Application(AbstractApplication):	
	domain 	 = models.ForeignKey(Domain)
