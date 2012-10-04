from django.conf.urls.defaults import patterns, include, url
from filebrowser.sites import site
from django.contrib import admin
admin.autodiscover()
import settings


urlpatterns = patterns('',
    url(r'^achievements/', include('achievements.urls', namespace='achievements')),
    url(r'^admin/filebrowser/', include(site.urls)),
    url(r'^admin/', include(admin.site.urls)),
    (r'^admin/jsi18n', 'django.views.i18n.javascript_catalog'),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)