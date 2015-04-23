from django.apps import AppConfig
from django.contrib import admin
from django.contrib.auth.models import Group

class ContribAuthConfig(AppConfig):
	name = 'django.contrib.auth'

	def ready(self):
		super().ready()
		admin.site.unregister(Group)