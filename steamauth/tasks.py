import json
import requests
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from celery.task import task


API_PROFILE_URL = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"


@task
def update_profiles(user_ids):
	users = get_user_model().objects.filter(id__in=user_ids)
	steamids = users.values_list('steamid', flat=True)
	r = requests.get(API_PROFILE_URL, params={
		"steamids": ",".join([str(i) for i in steamids]),
		"key": getattr(settings, 'STEAM_WEBAPI_KEY', None),
	})

	if r.status_code == requests.codes.ok and r.json:
		for player in r.json()['response']['players']:
			try:
				user = get_user_model().objects.filter(id__in=users).get(steamid=player['steamid'])
			except get_user_model().DoesNotExist:
				continue
			else:
				if not user.freeze_username:
					user.username = player['personaname']
				user.profile_url = player['profileurl']
				user.avatar = player['avatar']
				user.avatar_full = player['avatarfull']
				user.save()


@task
def update_presence(user_steamids):
	r = requests.get(API_PROFILE_URL, params={
		"steamids": ",".join([str(i) for i in user_steamids]),
		"key": getattr(settings, 'STEAM_WEBAPI_KEY', None),
	})

	if r.status_code == requests.codes.ok and r.json:
		for player in r.json()['response']['players']:
			try:
				user = get_user_model().objects.get(steamid=player['steamid'])
			except get_user_model().DoesNotExist:
				continue
			else:
				cache.set('user_{0}_state'.format(player['steamid']),
					player['personastate'], 600)
				cache.set('user_{0}_game'.format(player['steamid']),
					player['gameextrainfo'] if 'gameextrainfo' in player else None, 600)
