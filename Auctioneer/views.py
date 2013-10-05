# Create your views here.
from models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.shortcuts import render_to_response


def home(request):
    title = 'Home'
    links = [{'name': 'Home', 'target': '/auctioneer/home/'},
             {'name': 'Login', 'target': '/auctioneer/login/'},
             {'name': 'Search', 'target': '/auctioneer/search/'}]
    content = Auctions.get_latest()
    if content is None:
        return render_to_response('message.html', {'title': title, 'link_list': links, 'message': 'No content found!'},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('main.html', {'title': title, 'link_list': links, 'content_list': content},
                              context_instance=RequestContext(request))