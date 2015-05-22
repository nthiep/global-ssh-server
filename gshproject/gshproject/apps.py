from django.apps import AppConfig
from node.models import Machine, Gateway
from server.models import Session


class MyAppConfig(AppConfig):
	name = 'gshproject'
	verbose_name = "GSH Application"
	def ready(self):
		Machine.objects.all().delete()
		Gateway.objects.all().delete()
		Session.objects.all().delete()

