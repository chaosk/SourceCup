from django.conf.urls import include, url
from django.contrib import admin

from . import views

urlpatterns = [
	url(r'^t/(?P<slug>[\w-]+)/$', views.tournament_details, name='tournament_details'),
	url(r'^t/(?P<slug>[\w-]+)/join/$', views.tournament_join, name='tournament_join'),
	url(r'^t/(?P<slug>[\w-]+)/fixtures/$', views.tournament_details_fixtures,
			name='tournament_details_fixtures'),
	url(r'^t/(?P<slug>[\w-]+)/(?P<page>\w+)/$', views.tournament_details, name='tournament_details'),
	url(r'^t/(?P<slug>[\w-]+)/results/(?P<round_number>\d+)/$', views.tournament_details_results,
			name='tournament_details_results'),
	url(r'^tournaments/$', views.tournament_list, name='tournament_list'),
	url(r'^team/(?P<team_id>\d+)/$', views.team_details, name='team_details'),
	url(r'^team/(?P<team_id>\d+)/leave/$', views.team_leave, name='team_leave'),
	url(r'^team/(?P<team_id>\d+)/disband/$', views.team_disband, name='team_disband'),
	url(r'^team/(?P<team_id>\d+)/modify/$', views.team_edit, name='team_edit'),
	url(r'^team/(?P<team_id>\d+)/join/$', views.team_join, name='team_join'),
	url(r'^team/\+/$', views.team_create, name='team_create'),
]
