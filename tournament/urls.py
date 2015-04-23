from django.conf.urls import include, url
from django.contrib import admin

from . import views

urlpatterns = [
	url(r'^t/(?P<slug>[\w-]+)/$', views.tournament_details, name='tournament_details'),
	url(r'^t/(?P<slug>[\w-]+)/fixtures/$', views.tournament_details_fixtures,
			name='tournament_details_fixtures'),
	url(r'^t/(?P<slug>[\w-]+)/(?P<page>\w+)/$', views.tournament_details, name='tournament_details'),
	url(r'^t/(?P<slug>[\w-]+)/results/(?P<round_number>\d+)/$', views.tournament_details_results,
			name='tournament_details_results'),
	url(r'^tournaments/$', views.tournament_list, name='tournament_list'),
]
