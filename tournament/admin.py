from django.contrib import admin
from .models import TournamentBase, Season, Tournament, Region
from .models import Team, TeamEntry, Round


class TournamentInline(admin.TabularInline):
	model = Tournament
	extra = 1


@admin.register(TournamentBase)
class TournamentBaseAdmin(admin.ModelAdmin):
	pass


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
	inlines = [TournamentInline]


class TeamInline(admin.TabularInline):
	model = TeamEntry
	fields = ['team', 'is_ready', 'is_suspended', 'rank']
	readonly_fields = ['is_ready', 'is_suspended', 'rank']
	ordering = ['rank']

	def has_add_permission(self, request):
		return False


class RoundInline(admin.TabularInline):
	model = Round
	fields = ['number', 'map', 'starts_at', 'ends_at', 'is_scheduled', 'is_postprocessed', 'round_type']
	readonly_fields = ['number', 'starts_at', 'ends_at', 'is_scheduled', 'is_postprocessed', 'round_type']
	ordering = ['number']

	def has_add_permission(self, request):
		return False


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
	readonly_fields = ['season', 'region', 'name', 'short_name', 'slug']
	inlines = [RoundInline, TeamInline]


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
	pass


class MemberInline(admin.TabularInline):
	model = Team.members.through
	extra = 1


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
	inlines = [MemberInline]
	list_display = ['name', 'tag', 'leader']
