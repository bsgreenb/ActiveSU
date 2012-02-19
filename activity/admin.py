__author__ = 'rui'

from django.contrib import admin
from django_activity.activity.models import *

admin.site.register(UserProfile)
admin.site.register(Activity_Page)
admin.site.register(Activity_Page_User)
admin.site.register(Post)
admin.site.register(Text_Post)
admin.site.register(Event_Post)
admin.site.register(Comment)
