from django.db import models
from django.contrib.auth.models import User
from api.utils import create_auth_client, create_domain
from django.db.models.signals import post_save
from manage.models import Domain
# Create your models here.

post_save.connect(create_domain, sender=User)
post_save.connect(create_auth_client, sender=Domain)
