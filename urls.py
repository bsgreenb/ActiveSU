from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, password_reset, password_reset_done, password_reset_confirm, password_reset_complete, password_change, password_change_done
from django.contrib import admin
admin.autodiscover()

from activity.custom_decorator import anonymous_required
from activity import views





urlpatterns = patterns('',
    (r'^$', views.main_page),
)
