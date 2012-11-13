from django.conf.urls.defaults import patterns, include, url
from filebrowser.sites import site
from django.contrib import admin
admin.autodiscover()
import settings

urlpatterns = patterns('',
    # including urls which are needed in the views.py (achievements.urls)
    url(r'^achievements/', include('achievements.urls', namespace='achievements')),
    # url for activating filebrowser in admin site
    url(r'^admin/filebrowser/', include(site.urls)),
    # url for activating Django admin site
    url(r'^admin/', include(admin.site.urls)),
    #(r'^admin/jsi18n', 'django.views.i18n.javascript_catalog'),
    # url for media path in filebrowser
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)