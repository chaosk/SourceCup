from django.conf.urls import include, url
from django.contrib import admin
from .views import home

urlpatterns = [
	# Examples:
	# url(r'^$', 'SourceCup.views.home', name='home'),
	# url(r'^blog/', include('blog.urls')),
	url(r'', include('steamauth.urls')),
	url(r'', include('tournament.urls')),
	url(r'^$', home, name='home'),

	url(r'^autocomplete/', include('autocomplete_light.urls')),
	url(r'^admin/', include(admin.site.urls)),
]
