import autocomplete_light
from steamauth.models import SteamUser


class UserAutocomplete(autocomplete_light.AutocompleteModelTemplate):
	search_fields = ('username', 'steamid')
	choice_template = 'steamauth/autocomplete/user.html'
	autocomplete_js_attributes = {
		'placeholder': 'Username/SteamID...'
	}


class StaffUserAutocomplete(autocomplete_light.AutocompleteModelTemplate):
	choices = (
		SteamUser.objects.filter(level__gte=SteamUser.LEVEL_SIDEKICK)
	)
	search_fields = ('username', 'steamid')
	choice_template = 'steamauth/autocomplete/user.html'
	autocomplete_js_attributes = {
		'placeholder': 'Username/SteamID...'
	}

autocomplete_light.register(SteamUser, UserAutocomplete)
autocomplete_light.register(SteamUser, StaffUserAutocomplete)