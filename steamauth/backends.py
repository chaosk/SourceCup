import re
from django.contrib.auth import get_user_model
from openid.consumer.consumer import SUCCESS


STEAMID_PATTERN = re.compile(r"http:\/\/steamcommunity\.com\/openid\/id\/(?P<steamid>\d+)")


class SteamOpenIDBackend(object):

	def get_user(self, user_id):
		model = get_user_model()
		try:
			return model.objects.get(pk=user_id)
		except model.DoesNotExist:
			return None

	def authenticate(self, **kwargs):
		"""Authenticate the user based on an OpenID response."""
		# Require that the OpenID response be passed in as a keyword
		# argument, to make sure we don't match the username/password
		# calling conventions of authenticate.

		openid_response = kwargs.get('openid_response')
		if openid_response is None:
			return None

		if openid_response.status != SUCCESS:
			return None

		match = STEAMID_PATTERN.match(openid_response.identity_url)
		steamid = match.group('steamid')

		user, created = get_user_model().objects.get_or_create(
			steamid=int(steamid)
		)

		return user
