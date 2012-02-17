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
    (r'^password/change/$', password_change),
    (r'^password/change/done$', password_change_done),

    # change password
    url(r'^password/change/$', password_change),
    url(r'^password/change/done$', password_change_done),

    # reset password
    url(r'^accounts/password/reset/$', password_reset,{'post_reset_redirect' : '/accounts/password/reset/done/'}),
    url(r'^accounts/password/reset/done/$', password_reset_done),
    url(r'^accounts/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm,{'post_reset_redirect' : '/accounts/password/done/'}),
    url(r'^accounts/password/done/$', password_reset_complete),

    # core
    url(r'^$', views.main_page, name="main_page"),

    url(r'^submit_text_post$', views.submit_text_post, name="post_message"),
    url(r'^submit_event_post$', views.submit_event_post, name="post_event"),
    url(r'^submit_comment$', views.submit_comment, name='post_comment'),

    url(r'^(\w+)$', views.activity_page, name="activity_page"),
)
