from django.contrib import admin
from .models import SteamUser


@admin.register(SteamUser)
class SteamUserAdmin(admin.ModelAdmin):
	list_filter = ('level',)
