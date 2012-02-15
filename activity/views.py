from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login as auth_login, logout  #We want to avoid overriding our own login function
from django.contrib.auth.decorators import login_required


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





def main_page(request):
    return render_to_response('main_page.html', dict(), context_instance=RequestContext(request))

def activity_page(request):
    return render_to_response('activity_page.html', dict(), context_instance=RequestContext(request))





def create_post(request, type):
    if request.method == 'POST':
        if type == 'message':
            form = TextPostForm(request.POST)
            if form.is_valid():
                try:
                    activity_page = Activity_Page.objects.get(pk = form.cleaned_data['activity_page'])
                except Activity_Page.DoesNotExist:
                    return Http404

                new_post = Post.create(user = request.user, activity_page = activity_page)
                Text_Post.create(post = new_post, content = form.cleaned_data['content'])

                #TODO redirect to the right activity page

                return HttpResponseRedirect('/')

        elif type == 'event':
            form =


