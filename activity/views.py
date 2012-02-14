from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth import authenticate, login as auth_login, logout  #We want to avoid overriding our own login function
from django.contrib.auth.decorators import login_required


def main_page(request):
    return render_to_response('main_page.html', dict(), context_instance=RequestContext(request))

