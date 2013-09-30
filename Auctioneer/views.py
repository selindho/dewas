# Create your views here.
from models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.shortcuts import render_to_response


def home(request):
    title = 'Home'
    content = Auctions.get_latest()
    return render_to_response('main.html', {'title':title, 'content_list':content},
                              context_instance=RequestContext(request))