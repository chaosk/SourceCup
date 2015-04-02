import django.dispatch


openid_login_complete = django.dispatch.Signal(providing_args=[
	'request', 'openid_response'])
