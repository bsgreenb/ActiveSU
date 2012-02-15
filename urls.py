from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, password_reset, password_reset_done, password_reset_confirm, password_reset_complete, password_change, password_change_done
from django.contrib import admin

from activity.custom_decorator import anonymous_required
from activity import views



admin.autodiscover()


urlpatterns = patterns('',
    # admin
    url(r'^admin/', include(admin.site.urls)),

    # auth (give name to the url so that we can use {% url name %} in templates and reverse in view.
    url(r'^accounts/login/$', anonymous_required(login), name="login"),
    url(r'^register/$', anonymous_required(views.register_page, '/'), name="register"),
    url(r'^logout/$', views.logout_page, name="logout"),


    # core
    url(r'^$', views.main_page, name="main_page"),
    (r'^event/$', views.activity_page),
)
