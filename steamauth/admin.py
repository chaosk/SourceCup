from django.contrib import admin
from hijack.admin import HijackUserAdminMixin
from .models import SteamUser


@admin.register(SteamUser)
class SteamUserAdmin(admin.ModelAdmin, HijackUserAdminMixin):
	list_filter = ('level',)
	list_display = ('steamid', 'username', 'hijack_field')
	fields = ('steamid', 'email', 'wants_emails', 'freeze_username', 'is_active', 'level')
