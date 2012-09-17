from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from models import Category
from views import Overview

urlpatterns = patterns('achievements.views',
    url(r'^$', 'Overview', name='overview'),
    url(r'^(?P<category_id>\d+)/$', 'CategoryView', name='category'),
)

urlpatterns += staticfiles_urlpatterns()