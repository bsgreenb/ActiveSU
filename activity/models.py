from django.db import models
from django.db.models import Max, Count
from django.contrib.auth.models import User

from utils import ReverseManager

#from django.db import connection #for debugging

#Hmm lets see.  We want to get the Activity_Page LEFT JOIN (Post 
#

def get_activities_with_top_posts():
    """Returns all activities with their most recent posts.  We use raw SQL because django 1.3 doesn't have prefetch_related().  This is the only way to do it in one query."""
    return Activity_Page.objects.raw('''
    SELECT activity_activity_page.name, activity_activity_page.url_code,
    posts.*
    auth_user.username,
    activity_text_post.content,
    activity_event_post.title
    FROM
    activity_activity_page
    LEFT JOIN
    (
        SELECT activity_post.activity_page_id, activity_post.event_time,
        auth_user.username,
        activity_text_post.content,
        activity_event_post.title
        FROM
        activity_post
         ON activity_post.activity_page_id = activity_activity_page.id
        LEFT JOIN
        activity_text_post
         ON activity_post.id = activity_text_post.post_id
        LEFT JOIN
        activity_event_post
         ON activity_post.id = activity_event_post.post_id
    ) as posts
     ON posts.activity_page_id = activity_activity_page.id
    ''')

class Activity_Page(models.Model):
    name = models.CharField(max_length=50)
    url_code = models.CharField(max_length=50) #This is the basis for the pretty url 
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
        return Post.objects.filter(activity_page=self).select_related().order_by('-post_time', '-comment__comment_time')
 

    def get_future_events_and_comments(self):
        """
        Gets all future events for the activity page, ordered by when the event will happen, not when it was posted. Also gets the comments for those events
        """
        #TODO: This is proly wrong
        return Event_Post.objects.filter(post__activity_page=self).order_by('start_datetime', '-comment__comment_time')

    #Reverse manager so we can prefetch all the posts
    objects = models.Manager()
    reversemanager = ReverseManager({'posts': 'post_set'})

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
        return self.post + ':' + self.where + ' @ ' + self.when

class Comment(models.Model):
    user = models.ForeignKey(User)
    post = models.ForeignKey(Post)
    content = models.CharField(max_length=250)
    comment_time = models.DateTimeField(auto_now_add = True)

    def __unicode__(self):
        return 'Comment by ' + self.user + ' on ' + self.post + ':' + self.content
