from django.db import models
from django.contrib.auth.models import User

#from django.db import connection #for debugging

#Hmm lets see.  We want to get the Activity_Page LEFT JOIN (Post 
#

#Gets the activity pages, and the most recent activity post of each
def get_main_page():
    #TODO: Gotta get this right per SO
    return Activity_Page.objects.filter(enabled=True).annotate(Max('-post_time'),user_count = Count('users')).order_by('user_count')

class Activity_Page(models.Model):
    name = models.CharField(max_length=50)
    url_code = models.CharField(max_length=50) #This is the basis for the pretty url 
    created = models.DateTimeField(auto_now_add = True)
    enabled = models.BooleanField(default = True)
    users = models.ManyToManyField(User, through='Activity_Page_Users')

    def __unicode__(self):
        return self.name

    def get_posts_and_comments(self):
        """
        Get all posts (and comments on them) for the activity page, ordered by when they were posted.
        """
        #TODO: Same issue as above, not sure I'm doing this right..
        return Post.objects.filter(activity_page=self).select_related().prefetch_related('comment_set').order_by('-post_time', '-comment__comment_time')
 

    def get_future_events_and_comments(self):
        """
        Gets all future events for the activity page, ordered by when the event will happen, not when it was posted. Also gets the comments for those events
        """
        return Event_Post.objects.filter(post__activity_page=self).prefetch_related('comment_set').order_by('-post_time', '-comment__comment_time')

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
    when = models.DateTimeField()
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
