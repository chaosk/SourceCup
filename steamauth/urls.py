from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^signin/$', views.login_begin, name='signin'),
	url(r'^hello/$', views.login_complete, name='signed-in'),
	url(r'^bye/$', views.logout, name='signout'),
	url(r'^u/(?P<steamid>\d+)/$', views.user_details, name='user_details'),
]
