from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login as auth_login, logout  #We want to avoid overriding our own login function
from django.contrib.auth.decorators import login_required

from activity.forms import RegistrationForm

@login_required
def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')

def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                username = form.cleaned_data['email'].split['@'][0], #email prefix
                password = form.cleaned_data['password1'],
                email = form.cleaned_data['email']
            )

            new_user = authenticate(username = request.POST['username'], password=request.POST['password1'])
            auth_login(request, new_user)
            return HttpResponseRedirect(reverse('main_page'))
    else:
        form = RegistrationForm()

    return render_to_response('registration/register.html', dict(form = form), context_instance=RequestContext(request))

#TODO: update the template once I figure this one out
def main_page(request):
    activities = get_main_page()
    return render_to_response('main_page.html', dict(activities = activities), context_instance=RequestContext(request))

#TODO: Definitely need no posts / no events / no users messages
def activity_page(request, activity_url):
    try:
        activity_page = Activity_Page.get(url_code = activity_url)
    except DoesNotExist:
        return HttpResponseRedirect(reverse('main_page'))

    activity_page_users = activity_page.user_set 
    
    # We want to get all the posts, with comments, ordered by their post date
    all_posts = activity_page.get_posts_and_comments()

    # We want to get future events, ordered by their occuring date
    future_events = activity_page.get_future_events_and_comments()

    return render_to_response('activity_page.html', dict(activity_page_users = activity_page_users, all_posts = all_posts, future_events = future_event), context_instance=RequestContext(request))

#TODO
def submit_comment(request):
    pass

#TODO: Will take both text and event posts
def submit_post(request):
    pass

