from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login as auth_login, logout  #We want to avoid overriding our own login function
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
from django.db import transaction

from activity.models import *
from activity.forms import RegistrationForm, TextPostForm

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

#TODO: need to get a model function to get the 
def main_page(request):
    return render_to_response('main_page.html', dict(), context_instance=RequestContext(request))

#TODO.  Need to decide how we do events vs all sorting.
def activity_page(request):
    return render_to_response('activity_page.html', dict(), context_instance=RequestContext(request))

#TODO
def submit_comment(request):
    pass

#TODO: Will take both text and event posts
def submit_post(request):
    pass




def create_post(request, type):

    def check_activity_page(page_number):
        try:
            activity_page = Activity_Page.objects.get(pk = page_number)
        except Activity_Page.DoesNotExist:
            results = {
                'status':'invalid page.'
            }
            return HttpResponse(simplejson.dumps(results), 'application/javascript')
        else:
            return activity_page

    if request.is_ajax():
        if type == 'message':
            form = TextPostForm(request.POST)
            if form.is_valid():
                activity_page = check_activity_page(form.cleaned_data['activity_page'])
                with transaction.commit_on_success():
                    new_post = Post(user = request.user, activity_page = activity_page)
                    new_post.save()

                    new_text_post = Text_Post(post = new_post, content = form.cleaned_data['content'])
                    new_text_post.save()

                results = {
                    'status':'OK'
                }
                return HttpResponse(simplejson.dumps(results), 'application/javascript')
            else:
                results = {
                    'stauts':'invalid post.'
                }
                return HttpResponse(simplejson.dumps(results), 'application/javascript')


        elif type == 'event':
            form = EventPostForm(request.POST)
            if form.is_valid():
                activity_page = check_activity_page(form.cleaned_data['activity_page'])
                with transaction.commit_on_success():
                    new_post = Post(user = request.user, activity_page = activity_page)
                    new_post.save()

                    #TODO how to add those two times
                    start_datetime = form.cleaned_data['start_date'] + form.cleaned_data['start_time']

                    if form.cleaned_data.get('end_date', '') and form.cleaned_data.get('end_time', ''):
                        end_datetime = form.cleaned_data['end_date'] + form.cleaned_data['start_time']
                    else:
                        end_datetime = ''

                    Event_Post.create(
                        post = new_post,
                        where = form.cleaned_data['where'],
                        start_datetime = start_datetime,
                        end_datetime = end_datetime,
                        description = form.cleaned_data['description']
                    )

                results = {
                    'status':'OK'
                }
                return HttpResponse(simplejson.dumps(results), 'application/javascript')

            else:
                results = {
                    'status':'error',
                    'data':form.errors
                }
                return HttpResponse(simplejson.dumps(results), 'application/javascript')
    else:
        return HttpResponse(simplejson.dumps({'status':'invalid request'}))





