__author__ = 'rui'

from django.contrib import admin
from django_activity.activity.models import *

'''
class Activity_PageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class Activity_Page_UsersAdmin(admin.ModelAdmin):
    list_display = ('activity_page', 'user')

class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_page')

class Text_PostAdmin(admin.ModelAdmin):
    list_display = ('post', 'content')

class Event_PostAdmin(admin.ModelAdmin):
    list_display = ('post', 'where', 'start_datetime', 'end_datetime', 'description')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'content')
'''

admin.site.register(Activity_Page)
admin.site.register(Activity_Page_User)
admin.site.register(Post)
admin.site.register(Text_Post)
admin.site.register(Event_Post)
admin.site.register(Comment)
