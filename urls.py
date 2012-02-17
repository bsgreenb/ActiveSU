from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, password_reset, password_reset_done, password_reset_confirm, password_reset_complete, password_change, password_change_done
from django.contrib import admin
from django.views.generic.simple import direct_to_template

from activity.custom_decorator import anonymous_required
from activity import views


admin.autodiscover()


urlpatterns = patterns('',
    # admin
    url(r'^admin/', include(admin.site.urls)),

    # login (give name to the url so that we can use {% url name %} in templates and reverse in view.
    url(r'^accounts/login/$', anonymous_required(login), name="login"),

    # register
    url(r'^register/$', anonymous_required(views.register_page, '/'), name="register"),
    url(r'^register/confirm/$', direct_to_template, {'template':'registration/register_confirm.html'}, name="register_confirm"),
    url(r'register/success/(?P<confirmation_code>[0-9A-Za-z]+)/(?P<username>.+)/$', views.confirm),

    url(r'^logout/$', views.logout_page, name="logout"),
    (r'^password/change/$', password_change),
    (r'^password/change/done/$', password_change_done),

    # change password
    url(r'^password/change/$', password_change),
    url(r'^password/change/done/$', password_change_done),

    # reset password
    url(r'^accounts/password/reset/$', password_reset,{'post_reset_redirect' : '/accounts/password/reset/done/'}),
    url(r'^accounts/password/reset/done/$', password_reset_done),
    url(r'^accounts/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm,{'post_reset_redirect' : '/accounts/password/done/'}),
    url(r'^accounts/password/done/$', password_reset_complete),

    # core
    url(r'^$', views.main_page, name="main_page"),
    url(r'^(\w+)$', views.activity_page, name="activity_page"),


    url(r'^postmessage/$', views.submit_post, {'type':'message'}, name="post_message"),
    url(r'^postevent/$', views.submit_post, {'type':'event'}, name="post_event"),
)
