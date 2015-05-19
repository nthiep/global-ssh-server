from node.models import Gateway
from django.contrib.gis.utils import GeoIP

def create_gateway(sender, instance=None, created=False, **kwargs):
	""" create root domain of user """
	if created:
	geo = GeoIP()
	data = geo.city(instance.ip)
		instance.city = data['city']
	instance.country = data['country_name']
	instance.save()