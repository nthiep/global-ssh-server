from django.conf.urls import patterns, include, url
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# import app
import api.views
import pages.urls
import api.urls

# rest_framework
from rest_framework import routers
router = routers.DefaultRouter()
router.register(r'users',  api.views.UserViewSet)
router.register(r'groups', api.views.GroupViewSet)

handler500 = 'pages.views.handler404'
handler404 = 'pages.views.handler404'
# urlpatterns
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'gshproject.views.home', name='home'),
    # url(r'^gshproject/', include('gshproject.foo.urls')),

    url(r'^admin/', include(admin.site.urls)),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^', include(pages.urls)),
    url(r'^api/', include(api.urls)),
    # rest_framework url
    url(r'^api/', include(router.urls)),
    url(r'^api/', include('rest_framework.urls', namespace='rest_framework'))
    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
