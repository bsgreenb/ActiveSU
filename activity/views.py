import datetime

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login as auth_login, logout  #We want to avoid overriding our own login function
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
from django.db import transaction

from activity.models import *
from activity.forms import RegistrationForm, TextPostForm, EventPostForm

@login_required
def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')

def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                username = form.cleaned_data['email'].split('@')[0], #email prefix
                password = form.cleaned_data['password1'],
                email = form.cleaned_data['email']
            )

            new_user = authenticate(username = request.POST['email'], password=request.POST['password1'])
            auth_login(request, new_user)
            return HttpResponseRedirect(reverse('main_page'))
    else:
        form = RegistrationForm()

    return render_to_response('registration/register.html', dict(form = form), context_instance=RequestContext(request))

#TODO: update the template once I figure this one out
def main_page(request):
    #TODO: Gotta get this right per SO
    #TODO: http://stackoverflow.com/questions/6194589/django-create-filter-for-nice-time
    activities = Activity_Page.objects.filter(enabled=True).annotate(Max('post__post_time'),user_count = Count('users')).select_related().order_by('-user_count') #Gets the activity pages, and the most recent activity post of each
    
    return render_to_response('main_page.html', dict(activities = activities), context_instance=RequestContext(request))

#TODO: Definitely need no posts / no events / no users message
#TODO: Also need messages for not logged in users
def activity_page(request, activity_url):
    try:
        activity_page = Activity_Page.objects.get(url_code = activity_url)
    except Activity_Page.DoesNotExist:
        return HttpResponseRedirect(reverse('main_page'))

    #If they're logged in and not a user of this page, we want to make them a user
    if request.user.is_authenticated():
        Activity_Page_User.objects.get_or_create(user = request.user, activity_page = activity_page)

    #Get users of this page
    activity_page_users = activity_page.users
    
    # We want to get all the posts, with comments, ordered by their post date
    all_posts = activity_page.get_posts_and_comments()

    # We want to get future events, ordered by their occuring date
    future_events = activity_page.get_future_events_and_comments()

    if request.session.get('message_form_with_error', ''):
        message_form_with_error = request.session['message_form_with_error']
        del request.session['message_form_with_error']
    else:
        message_form_with_error = ''

    if request.session.get('event_form_with_error', ''):
        event_form_with_error = request.session['event_form_with_error']
        del request.session['event_form_with_error']
    else:
        event_form_with_error = ''

    return render_to_response('activity_page.html', dict(activity_page = activity_page, activity_page_users = activity_page_users, all_posts = all_posts, future_events = future_events, message_form_with_error = message_form_with_error, event_form_with_error = event_form_with_error), context_instance=RequestContext(request))

#Note: We currently assume that they're a member of the page, but in later versions we might have to think out a more complex system for joining and leaving of pages.
@login_required
def submit_comment(request):
    if request.is_ajax() and request.method == 'POST':
        result = []
        form = CommentPostForm(request.POST) #TODO: Create this form
        if form.is_valid():
            post = form.cleaned_data['post']
            content = form.cleaned_data['content']
            Comment.create(user = request.user, post = post, content = content)
            result['status'] = 'OK'
        else:
            result['status'] = 'invalid'
    
        return HttpResponse(simplejson.dumps(results))
    else:
        return Http404

#TODO: Possibly split into two.. qstn: model form issues?
#TODO: Will take both text and event posts
@login_required
def submit_post(request, type):

    if request.method == 'POST':
        try:
            activity_page = Activity_Page.objects.get(pk = request.POST['activity_page'])
        except Activity_Page.DoesNotExist:
            return Http404

        if type == 'message':
            form = TextPostForm(request.POST)
            if form.is_valid():
                with transaction.commit_on_success():
                    new_post = Post(user = request.user, activity_page = activity_page)
                    new_post.save()

                    new_text_post = Text_Post(post = new_post, content = form.cleaned_data['content'])
                    new_text_post.save()
            else:
                request.session['message_form_with_error'] = form

            return HttpResponseRedirect(reverse('activity_page', args=[activity_page.url_code]))

        elif type == 'event':
            form = EventPostForm(request.POST)
            if form.is_valid():
                with transaction.commit_on_success():
                    new_post = Post(user = request.user, activity_page = activity_page)
                    new_post.save()

                    #TODO how to add those two times

                    start_datetime = form.cleaned_data['start_date'] + datetime.timedelta(minutes = form.cleaned_data['start_time'])

                    if form.cleaned_data.get('end_date', '') and form.cleaned_data.get('end_time', ''):
                        end_datetime = form.cleaned_data['end_date'] + datetime.timedelta(minutes = form.cleaned_data['end_time'])
                    else:
                        end_datetime = None

                    new_event_post = Event_Post(
                        post = new_post,
                        title = form.cleaned_data['title'],
                        where = form.cleaned_data['where'],
                        start_datetime = start_datetime,
                        end_datetime = end_datetime,
                        description = form.cleaned_data['description']
                    )
                    new_event_post.save()
            else:

                request.session['event_form_with_error'] = form

            return HttpResponseRedirect(reverse('activity_page', args=[activity_page.url_code]))

    return HttpResponseRedirect(reverse('main_page'))





