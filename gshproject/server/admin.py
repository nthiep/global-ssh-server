from django.contrib import admin
from .models import Session, UDPSession, RelaySession
# Register your models here.
admin.site.register(Session)
admin.site.register(UDPSession)
admin.site.register(RelaySession)
