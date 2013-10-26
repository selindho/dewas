# Create your views here.
from Auctioneer.models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User, Group, Permission
from django.db import IntegrityError


def home(request):
    content = Auctions.get_latest()
    is_logged_in = request.user.is_authenticated()
    return render_to_response('main.html', {'title': 'Home', 'is_logged_in': is_logged_in, 'content_list': content},
                              context_instance=RequestContext(request))


def sign_up(request):
    is_logged_in = request.user.is_authenticated()

    if request.method == 'POST':
        if 'email' in request.POST and 'username' in request.POST and 'password' in request.POST:
            try:
                User.objects.create_user(email=request.POST['email'], username=request.POST['username'],
                                         password=request.POST['password'])
                return render_to_response('message.html', {'title': 'Success!', 'is_logged_in': is_logged_in,
                                                           'message': 'Account created!'},
                                          context_instance=RequestContext(request))
            except IntegrityError:
                return render_to_response('message.html', {'title': 'Error!', 'is_logged_in': is_logged_in,
                                                           'message': 'User exists!'},
                                          context_instance=RequestContext(request))

        else:
            return render_to_response('signup.html', {'title': 'Sign Up', 'is_logged_in': is_logged_in},
                                      context_instance=RequestContext(request))
    else:
        return render_to_response('signup.html', {'title': 'Sign Up', 'is_logged_in': is_logged_in},
                                  context_instance=RequestContext(request))


def auth(request):
    is_logged_in = request.user.is_authenticated()

    if request.method == 'POST':
        if 'username' in request.POST and 'password' in request.POST:
            user = authenticate(username=request.POST['username'], password=request.POST['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('/auctioneer/home/')
                else:
                    return render_to_response('message.html', {'title': 'Error!', 'is_logged_in': is_logged_in,
                                                               'message': 'Account suspended!'},
                                              context_instance=RequestContext(request))
            else:
                return render_to_response('message.html', {'title': 'Error!', 'is_logged_in': is_logged_in,
                                                           'message': 'Invalid credentials!'},
                                          context_instance=RequestContext(request))
        else:
            return render_to_response('auth.html', {'title': 'Login', 'is_logged_in': is_logged_in},
                                      context_instance=RequestContext(request))
    else:
        return render_to_response('auth.html', {'title': 'Login', 'is_logged_in': is_logged_in},
                                  context_instance=RequestContext(request))


def leave(request):
    logout(request)
    return HttpResponseRedirect('/auctioneer/home/')


def browse(request):
    is_logged_in = request.user.is_authenticated()
    if request.method == 'POST' and 'query' in request.POST:
        content = Auctions.get_by_query(request.POST['query'])
        return render_to_response('browse.html', {'title': 'Login', 'is_logged_in': is_logged_in, 'is_search': True,
                                                  'query': request.POST['query'], 'content_list': content},
                                  context_instance=RequestContext(request))
    else:
        content = Auctions.get_all()
        return render_to_response('browse.html', {'title': 'Login', 'is_logged_in': is_logged_in, 'is_search': False,
                                                  'content_list': content},
                                  context_instance=RequestContext(request))