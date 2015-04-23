import re
import urllib.parse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate
from django.contrib.auth import login as auth_login, get_user_model
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt

from openid.consumer.consumer import Consumer, SUCCESS, CANCEL, FAILURE
from openid.consumer.discover import DiscoveryFailure

from .store import DjangoOpenIDStore
from .signals import openid_login_complete
from .utils import HttpResponseReload, staff_member_required

next_url_re = re.compile('^/[-\w/]+$')


def is_valid_next_url(next):
	# When we allow this:
	#   /signin/?next=/welcome/
	# For security reasons we want to restrict the next= bit to being a local
	# path, not a complete URL.
	return bool(next_url_re.match(next))


def sanitise_redirect_url(redirect_to):
	"""Sanitise the redirection URL."""
	# Light security check -- make sure redirect_to isn't garbage.
	is_valid = True
	if not redirect_to or ' ' in redirect_to or '//' in redirect_to:
		is_valid = False

	# If the return_to URL is not valid, use the default.
	if not is_valid:
		redirect_to = settings.LOGIN_REDIRECT_URL

	return redirect_to


def make_consumer(request):
	"""Create an OpenID Consumer object for the given Django request."""
	# Give the OpenID library its own space in the session object.
	session = request.session.setdefault('OPENID', {})
	store = DjangoOpenIDStore()
	return Consumer(session, store)


def parse_openid_response(request):
	"""Parse an OpenID response from a Django request."""
	# Short cut if there is no request parameters.
	#if len(request.REQUEST) == 0:
	#    return None

	current_url = request.build_absolute_uri()

	consumer = make_consumer(request)
	return consumer.complete(dict(request.REQUEST.items()), current_url)


def login_begin(request):
	"""Begin an OpenID login request, possibly asking for an identity URL."""
	redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '')

	openid_url = getattr(settings, 'STEAM_PROVIDER_URL', None)

	consumer = make_consumer(request)
	try:
		openid_request = consumer.begin(openid_url)
	except DiscoveryFailure as exc:
		messages.error(request, "OpenID discovery error: {0}".format(str(exc)))
		return HttpResponseReload(request)

	# Construct the request completion URL, including the page we
	# should redirect to.
	return_to = request.build_absolute_uri(reverse('signed-in'))
	if redirect_to:
		if '?' in return_to:
			return_to += '&'
		else:
			return_to += '?'
		return_to += urllib.parse.urlencode({REDIRECT_FIELD_NAME: redirect_to})

	trust_root = request.build_absolute_uri('/')

	redirect_url = openid_request.redirectURL(
		trust_root, return_to)
	return HttpResponseRedirect(redirect_url)


@csrf_exempt
def login_complete(request):
	redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '')

	openid_response = parse_openid_response(request)
	if not openid_response:
		messages.error(request, "This is an OpenID relying party endpoint.")
		return HttpResponseReload(request)

	if openid_response.status == SUCCESS:
		user = authenticate(openid_response=openid_response)

		if user is not None:
			if user.is_active:
				auth_login(request, user)
				messages.success(request, "Hello!")
				openid_login_complete.send(sender=get_user_model(),
					request=request, openid_response=openid_response)
				return HttpResponseRedirect(sanitise_redirect_url(redirect_to))
			else:
				messages.error(request, "Account has been disabled.")
				return HttpResponseReload(request)
		else:
			messages.error(request, "Unknown user.")
			return HttpResponseReload(request)
	elif openid_response.status == FAILURE:
		messages.error(request,
			"OpenID authentication failed: {0}".format(openid_response.message))
		return HttpResponseReload(request)
	elif openid_response.status == CANCEL:
		messages.error(request,
			"Authentication process has been cancelled by client.")
		return HttpResponseReload(request)
	else:
		assert False, (
			"Unknown OpenID response type: %r" % openid_response.status)


def logout(request):
	auth_logout(request)
	messages.info(request, "Bye!")
	return HttpResponseReload(request)


def user_details(request, steamid):
	user = get_object_or_404(get_user_model(), steamid=steamid)

	return render(request, 'steamauth/user_details.html', {
		'auser': user,
	})
