import datetime

from django.db import models
from django.db.models import Max, Count
from django.contrib.auth.models import User

class UserProfile(models.Model):  # it's used for registration confirmation email.
    user = models.OneToOneField(User)
    confirmation_code = models.CharField(max_length = 33)
    subscribe = models.BooleanField(default = True)
    unsubscribe_code = models.CharField(max_length = 33)

    def __unicode__(self):
        return self.user.username

class Activity_Page(models.Model):
    name = models.CharField(max_length=50)
    url_code = models.CharField(max_length=50) #This is the basis for the pretty url
    show_email = models.BooleanField(default = False)
    created = models.DateTimeField(auto_now_add = True)
    enabled = models.BooleanField(default = True)
    users = models.ManyToManyField(User, through='Activity_Page_User')

    def __unicode__(self):
        return self.name

    def get_posts_and_comments(self):
        """
        Get all posts (and comments on them) for the activity page, ordered by when they were posted.
        """
        #TODO: Same issue as above, not sure I'm doing this right..
        return Post.objects.filter(activity_page=self).select_related().order_by('-post_time')
 

    def get_future_events_and_comments(self):
        """
        Gets all future events for the activity page, ordered by when the event will happen, not when it was posted. Also gets the comments for those events
        """
        #TODO. would this cause problem ????
        return Event_Post.objects.filter(post__activity_page=self, start_datetime__gt=datetime.datetime.now().date()).select_related().order_by('start_datetime', 'post__comment__comment_time')

class Activity_Page_User(models.Model):
    activity_page = models.ForeignKey(Activity_Page)
    user = models.ForeignKey(User)
    join_time = models.DateTimeField(auto_now_add = True)

#Note: make sure to use a transaction when creating posts, becase we need to ensure that both the Post and specific Post_Type are inserted fine.
class Post(models.Model):
    user = models.ForeignKey(User)
    activity_page = models.ForeignKey(Activity_Page)
    post_time = models.DateTimeField(auto_now_add = True)
    
    def __unicode__(self):
        return 'Post by ' + unicode(self.user) + ' on ' + unicode(self.activity_page) + ' at ' + str(self.post_time)
    
    class Meta:
        get_latest_by = 'post_time'
        ordering = ['-post_time']

class Text_Post(models.Model):
    post = models.OneToOneField(Post)
    content = models.CharField(max_length=500)

    def __unicode__(self):
        return unicode(self.post) + ':' + self.content

class Event_Post(models.Model):
    post = models.OneToOneField(Post)
    title = models.CharField(max_length=100)
    where = models.CharField(max_length=200)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null = True, blank = True)
    description = models.CharField(max_length=300,null=True,blank=True)

    def __unicode__(self):
        return unicode(self.post) + ':' + self.where

class Comment(models.Model):
    user = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    content = models.CharField(max_length=250)
    comment_time = models.DateTimeField(auto_now_add = True)

    class Meta:
        ordering = ['comment_time']
    
    def __unicode__(self):
        return 'Comment by ' + str(self.user) + ' on ' + str(self.post) + ':' + self.content


