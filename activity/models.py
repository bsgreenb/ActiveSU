from django.db import models
from django.contrib.auth.models import User

#from django.db import connection #for debugging

class Activity_Page(models.Model):
    name = models.CharField(max_length=50) #This is also the basis for the pretty url
    created = models.DateTimeField(auto_now_add = True)
    enabled = models.BooleanField(default = True)
    users = models.ManyToManyField(User, through='Activity_Page_Users')

    def __unicode__(self):
        return self.name

    def get_all_posts_and_comments(self):
        """
        Get all posts (and comments on them) for the activity page, ordered by when they were posted.
        """
    def get_events_by_date(self):
        """
        Gets all events for the activity page, ordered by when the event will happen, not when it was posted. Also gets the comments for those events
        """

class Activity_Page_Users(models.Model):
    activity_page = models.ForeignKey(Activity_Page)
    user = models.ForeignKey(User)
    join_time = models.DateTimeField(auto_now_add = True)

#Note: make sure to use a transaction when creating posts, becase we need to ensure that both the Post and specific Post_Type are inserted fine.
class Post(models.Model):
    user = models.ForeignKey(User)
    activity_page = models.ForeignKey(Activity_Page)
    post_time = models.DateTimeField(auto_now_add = True)

    def __unicode__(self):
        return 'Post by ' + self.user + ' on ' + self.activity_page + ' at ' + self.post_time

class Text_Post(models.Model):
    post = models.OneToOneField(Post)
    content = models.CharField(max_length=500)

    def __unicode__(self):
        if self.target:
            return self.post + ' (at ' + self.target + '): ' + self.content
        else:
            return self.post + ':' + self.content

class Event_Post(models.Model):
    post = models.OneToOneField(Post)
    where = models.CharField(max_length=200)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null = True, blank = True)
    description = models.CharField(max_length=500)

    def __unicode__(self):
        return self.post + ':' + self.where + ' @ ' + self.when

class Comment(models.Model):
    user = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    content = models.CharField(max_length=250)
    comment_time = models.DateTimeField(auto_now_add = True)

    def __unicode__(self):
        return 'Comment by ' + self.user + ' on ' + self.post + ':' + self.content
