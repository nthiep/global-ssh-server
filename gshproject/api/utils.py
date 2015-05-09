
from manage.models import Application, Domain

def create_auth_client(sender, instance=None, created=False, **kwargs):
    """
    Intended to be used as a receiver function for a `post_save` signal 
    on a custom User model
    Creates client_id and client_secret for authenticated users
    """
    if created:
        Application.objects.create(domain=instance, user=instance,
                                   client_type=Application.CLIENT_CONFIDENTIAL,
                                   authorization_grant_type=Application.GRANT_PASSWORD)
def create_domain(sender, instance=None, created=False, **kwargs):
	""" create root domain of user """
	if created:
		Domain.objects.create(user=instance, domain="root." + instance.username, password=instance.password)