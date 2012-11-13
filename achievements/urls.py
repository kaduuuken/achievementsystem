from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from models import Category
from views import Overview

# urls for views in view.py
urlpatterns = patterns('achievements.views',
    # url for Overview
    url(r'^$', 'Overview', name='overview'),
    # url for CategoryView
    url(r'^(?P<category_id>\d+)/$', 'CategoryView', name='category'),
    # url for PositionModalView
    url(r'^position_remote/(?P<achievement_id>\d+)/$', 'PositionModalView', name='position_modal'),
    # url for TrophyModalView
    url(r'^trophy_remote/(?P<trophy_pos>\d+)/$', 'TrophyModalView', name='trophy_modal'),
    # url for TrophyView
    url(r'^(?P<trophy_slot>\d+)/(?P<achievement_id>\d+)/$', 'TrophyView', name='trophy'),
)

urlpatterns += staticfiles_urlpatterns()