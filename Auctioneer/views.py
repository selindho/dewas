# Create your views here.
from models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.models import User


def home(request):
    title = 'Home'
    links = [{'name': 'Home', 'target': '/auctioneer/home/'},
             {'name': 'Login', 'target': '/auctioneer/login/'},
             {'name': 'Sign Up', 'target': '/auctioneer/signup/'}]
    content = Auctions.get_latest()
    if content is None:
        return render_to_response('message.html', {'title': title, 'link_list': links, 'message': 'No content found!'},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('main.html', {'title': title, 'link_list': links, 'content_list': content},
                                  context_instance=RequestContext(request))


def sign_up(request):
    links = [{'name': 'Home', 'target': '/auctioneer/home/'},
             {'name': 'Login', 'target': '/auctioneer/login/'},
             {'name': 'Sign Up', 'target': '/auctioneer/signup/'}]
    if request.method == 'POST' and 'username' in request.POST and 'password' in request.POST:
        #User.objects.create_user()
        return render_to_response('message.html', {'title': 'Success!', 'link_list': links, 'message': 'User account created!'}, context_instance=RequestContext(request))
    else:
        return render_to_response('signup.html', {'title': 'Sign Up', 'link_list': links}, context_instance=RequestContext(request))