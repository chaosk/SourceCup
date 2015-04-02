from functools import wraps
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.views import login, REDIRECT_FIELD_NAME
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.utils.encoding import iri_to_uri


""" Well, magic. """
STEAMID_MAGIC = 76561197960265728


API_PERSONA_STATE_OFFLINE = 0
API_PERSONA_STATE_ONLINE = 1
API_PERSONA_STATE_BUSY = 2
API_PERSONA_STATE_AWAY = 3
API_PERSONA_STATE_SNOOZE = 4
API_PERSONA_STATE_LOOKINGTOTRADE = 5
API_PERSONA_STATE_LOOKINGTOPLAY = 6
API_PERSONA_STATES = (
	"Offline",
	"Online",
	"Busy",
	"Away",
	"Snooze",
	"Looking to Trade",
	"Looking to Play"
)
get_state_display = lambda n: API_PERSONA_STATES[n]


class HttpResponseReload(HttpResponse):
	"""
	Reload page and stay on the same page from where request was made.

	example:

	def simple_view(request):
		if request.POST:
			form = CommentForm(request.POST):
			if form.is_valid():
				form.save()
				return HttpResponseReload(request)
		else:
			form = CommentForm()
		return render_to_response('some_template.html', {'form': form})
	"""
	status_code = 302

	def __init__(self, request):
		HttpResponse.__init__(self)
		referer = request.META.get('HTTP_REFERER')
		self['Location'] = iri_to_uri(referer or "/")


def staff_member_required(view_func, login_url=None):
	"""
	Ensure that the user is a logged-in staff member.

	* If not authenticated, redirect to a specified login URL.
	* If not staff, show a 403 page

	This decorator is based on the decorator with the same name from
	django.contrib.admin.view.decorators.  This one is superior as it allows a
	redirect URL to be specified.
	"""

	@wraps(view_func)
	def _checklogin(request, *args, **kwargs):
		if request.user.is_active and request.user.is_staff:
			return view_func(request, *args, **kwargs)

		# If user is not logged in, redirect to login page
		if not request.user.is_authenticated():
			defaults = {
				'template_name': 'admin/login.html',
				'authentication_form': AdminAuthenticationForm,
				'extra_context': {
					'title': 'Log in',
					'app_path': request.get_full_path(),
					REDIRECT_FIELD_NAME: request.get_full_path(),
				},
			}
			return login(request, **defaults)
		else:
			# User does not have permission to view this page
			raise PermissionDenied

	return _checklogin
