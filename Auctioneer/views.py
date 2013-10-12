# Create your views here.
from models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.models import User


def get_links(isLoggedIn):
    if isLoggedIn:
        return [{'name': 'Home', 'target': '/auctioneer/home/'},
                {'name': 'My Auctions', 'target': '/auctioneer/account/auctions/'},
                {'name': 'Account', 'target': '/auctioneer/account/'},
                {'name': 'Logout', 'target': '/auctioneer/login/'}]
    else:
        return [{'name': 'Home', 'target': '/auctioneer/home/'},
                {'name': 'Login', 'target': '/auctioneer/login/'},
                {'name': 'Sign Up', 'target': '/auctioneer/signup/'}]


def home(request):
    content = Auctions.get_latest()
    isLoggedIn = request.user.is_authenticated()

    if content is None:
        return render_to_response('message.html', {'title': 'Home', 'link_list': get_links(isLoggedIn), 'message': 'No content found!'},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('main.html', {'title': 'Home', 'link_list': get_links(isLoggedIn), 'content_list': content},
                                  context_instance=RequestContext(request))


def sign_up(request):
    isLoggedIn = request.user.is_authenticated()

    if request.method == 'POST' and 'username' in request.POST and 'password' in request.POST:
        #User.objects.create_user()
        return render_to_response('message.html', {'title': 'Success!', 'link_list': get_links(isLoggedIn),
                                                   'message': 'User account created!'},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('signup.html', {'title': 'Sign Up', 'link_list': get_links(isLoggedIn)},
                                  context_instance=RequestContext(request))