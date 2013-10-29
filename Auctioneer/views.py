# Create your views here.
from django.contrib.auth.decorators import login_required
from Auctioneer.models import *
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from datetime import datetime, timedelta
import re
from django.core import mail
from django.core.mail import send_mail


def home(request):
    content = Auctions.get_nearest()
    is_logged_in = request.user.is_authenticated()
    return render_to_response('main.html', {'title': 'Home', 'is_logged_in': is_logged_in, 'tag': 'Upcoming auctions',
                                            'content_list': content},
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
    nxt = '/auctioneer/home/'

    if request.method == 'POST':
        if 'username' in request.POST and 'password' in request.POST:
            user = authenticate(username=request.POST['username'], password=request.POST['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if 'next' in request.POST:
                        nxt = request.POST['next']
                    return HttpResponseRedirect(nxt)
                else:
                    return render_to_response('message.html', {'title': 'Error!', 'is_logged_in': is_logged_in,
                                                               'message': 'Account suspended!'},
                                              context_instance=RequestContext(request))
            else:
                return render_to_response('message.html', {'title': 'Error!', 'is_logged_in': is_logged_in,
                                                           'message': 'Invalid credentials!'},
                                          context_instance=RequestContext(request))
        else:
            return render_to_response('auth.html', {'title': 'Login', 'is_logged_in': is_logged_in,
                                                    'next': '/auctioneer/home/'},
                                      context_instance=RequestContext(request))
    else:
        if request.method == 'GET' and 'next' in request.GET:
            nxt = request.GET['next']

        return render_to_response('auth.html', {'title': 'Login', 'is_logged_in': is_logged_in, 'next': nxt},
                                  context_instance=RequestContext(request))


def leave(request):
    logout(request)
    return HttpResponseRedirect('/auctioneer/home/')


def browse(request):
    is_logged_in = request.user.is_authenticated()
    if request.method == 'POST' and 'query' in request.POST:
        content = Auctions.get_by_query(request.POST['query'])
        return render_to_response('browse.html', {'title': 'Browse', 'is_logged_in': is_logged_in, 'is_search': True,
                                                  'query': request.POST['query'], 'content_list': content},
                                  context_instance=RequestContext(request))
    else:
        content = Auctions.get_all()
        return render_to_response('browse.html', {'title': 'Browse', 'is_logged_in': is_logged_in, 'is_search': False,
                                                  'content_list': content},
                                  context_instance=RequestContext(request))


@login_required
def account(request):
    is_logged_in = request.user.is_authenticated()
    user = request.user
    if request.method == 'POST' and 'email' in request.POST and 'password' in request.POST:
        user.email = request.POST['email']
        user.set_password(request.POST['password'])
        user.save()
        return render_to_response('message.html', {'title': 'Success!', 'is_logged_in': is_logged_in,
                                                   'message': 'Account updated!'},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('account.html', {'title': 'Account', 'is_logged_in': is_logged_in, 'user': user},
                                  context_instance=RequestContext(request))


@login_required
def create(request):
    is_logged_in = request.user.is_authenticated()

    if request.method == 'POST' and 'title' in request.POST and 'description' in request.POST and \
                         'start' in request.POST and 'stop' in request.POST and 'starting_price' in request.POST:
        try:
            start = datetime.strptime(request.POST['start'], '%Y-%m-%d %H:%M')
            stop = datetime.strptime(request.POST['stop'], '%Y-%m-%d %H:%M')
            exp = re.compile(r'^\d{1,10}(.\d{0,2})?$')
            result = exp.match(request.POST['starting_price'])
            if stop >= start + timedelta(days=3) and start >= datetime.now() and result is not None:
                shelf(request)
                return render_to_response('confirm.html', {'title': 'Confirmation', 'is_logged_in': is_logged_in,
                                                           'auction_title': request.POST['title'],
                                                           'description': request.POST['description'],
                                                           'starting_price': request.POST['starting_price'],
                                                           'start': request.POST['start'],
                                                           'stop': request.POST['stop']
                                                           },
                                          context_instance=RequestContext(request))
            else:
                return render_to_response('create.html', {'title': 'Create auction',
                                                          'is_logged_in': is_logged_in,
                                                          'message': 'Input error, try again!',
                                                          },
                                          context_instance=RequestContext(request))
        except:
            return render_to_response('create.html', {'title': 'Create auction',
                                                      'is_logged_in': is_logged_in,
                                                      'message': 'Input error, try again!',
                                                      },
                                      context_instance=RequestContext(request))
    else:
        return render_to_response('create.html', {'title': 'Create auction',
                                                  'is_logged_in': is_logged_in,
                                                  },
                                  context_instance=RequestContext(request))


@login_required
def confirm(request):
    is_logged_in = request.user.is_authenticated()
    user = request.user
    session = request.session

    if request.method == 'POST' and 'status' in request.POST and 'valid' in request.session:
        if request.POST['status'] == 'True' and session['valid'] == 'True':
            session['valid'] = 'False'
            new = Auctions(seller=user, title=session['title'], description=session['description'],
                           startingPrice=session['starting_price'], startDate=session['start'],
                           stopDate=session['stop'])
            new.save()
            send_mail('Auctioneer: Auction created!', 'Your auction ' + new.title + ' was created successfully!',
                      'auctioneer@some.mail', [new.seller.email], fail_silently=False)
            print 'Sent e-mail messages:'
            for message in mail.outbox:
                print message.subject
            return render_to_response('message.html', {'title': 'Success!', 'is_logged_in': is_logged_in,
                                                       'message': 'Auction created!'},
                                      context_instance=RequestContext(request))
        else:
            session['valid'] = 'False'
            return render_to_response('message.html', {'title': 'Canceled!', 'is_logged_in': is_logged_in,
                                                       'message': 'Auction creation was canceled!'},
                                      context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/auctioneer/home/')


def shelf(request):
        request.session['valid'] = 'True'
        request.session['title'] = request.POST['title']
        request.session['description'] = request.POST['description']
        request.session['start'] = request.POST['start']
        request.session['stop'] = request.POST['stop']
        request.session['starting_price'] = request.POST['starting_price']


@login_required
def auctions(request):
    is_logged_in = request.user.is_authenticated()
    content = Auctions.get_by_seller(request.user)
    return render_to_response('main.html', {'title': 'My Auctions', 'is_logged_in': is_logged_in,
                                            'tag': 'Auctions by '+request.user.username, 'content_list': content},
                              context_instance=RequestContext(request))


def details(request, auction_id):
    auction = Auctions.get_by_id(auction_id)
    is_logged_in = request.user.is_authenticated()

    if auction is not None:
        return render_to_response('details.html', {'title': 'Details', 'is_logged_in': is_logged_in,
                                                   'content': auction},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('message.html', {'title': 'Not found!', 'is_logged_in': is_logged_in,
                                                   'message': 'No such auction found!'},
                                  context_instance=RequestContext(request))

