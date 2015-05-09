from django.conf.urls import patterns, include, url
from api import views

urlpatterns = patterns('',
	url(r'^signup/$', views.SignUp.as_view(), name="signup"),
	url(r'^join/$', views.JoinDomain.as_view(), name="join"),
	url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
	url(r'^machine/$', views.MachineView.as_view(), name="machine"),
	url(r'^machine/info/$', views.MachineInfoView, name="machine_info"),
	url(r'^workgroup/$', views.WorkgroupView, name="workgroup"),
	url(r'^workgroup/authorization/$', views.AuthWorkgroupView, name="join_workgroup"),
	
	url(r'^authorization/$', views.AuthorizationView.as_view(), name="authorization"),

)

