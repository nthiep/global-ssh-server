from django.conf.urls import patterns, include, url
from pages import views
urlpatterns = patterns('',
	
	url(r'^$', views.index),
	url(r'^register/$', views.register),
	url(r'^login/$',  views.user_login),
	url(r'^logout/$', views.user_logout),
	url(r'^about/$', views.about),
	url(r'^dashboard/$', views.Dashboard),
	url(r'^domain/$', views.DomainView),
	url(r'^domain/edit/(?P<domain>\w+\.\w+)/$', views.DomainEditView),
	url(r'^domain/delete/(?P<domain>\w+\.\w+)/$', views.DomainDeleteView),
	url(r'^domain/add/$', views.DomainEditView),
	url(r'^machine/$', views.MachineView),
	url(r'^machine/(?P<domain>\w+\.\w+)/$', views.MachineView),
	url(r'^gateway/$', views.GatewayView),
	url(r'^gateway/(?P<domain>\w+\.\w+)/$', views.GatewayView),
	url(r'^gateway/(?P<gateway>\w+)/$', views.GatewayDetailView),
	url(r'^netmap/$', views.NetmapView),
	url(r'^netmap/(?P<domain>\w+\.\w+)/$', views.NetmapView),
)
