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
from django.core.mail import send_mail, send_mass_mail
from django.utils.translation import ugettext as _


def home(request):
    content = Auctions.get_nearest()
    is_logged_in = request.user.is_authenticated()
    return render_to_response('main.html', {'title': _('Home'), 'is_logged_in': is_logged_in,
                                            'tag': _('Upcoming auctions'), 'content_list': content},
                              context_instance=RequestContext(request))


def sign_up(request):
    is_logged_in = request.user.is_authenticated()

    if request.method == 'POST':
        if 'email' in request.POST and 'username' in request.POST and 'password' in request.POST:
            try:
                User.objects.create_user(email=request.POST['email'], username=request.POST['username'],
                                         password=request.POST['password'])
                return render_to_response('message.html', {'title': _('Success!'), 'is_logged_in': is_logged_in,
                                                           'message': _('Account created!')},
                                          context_instance=RequestContext(request))
            except IntegrityError:
                return render_to_response('message.html', {'title': _('Error!'), 'is_logged_in': is_logged_in,
                                                           'message': _('User exists!')},
                                          context_instance=RequestContext(request))

        else:
            return render_to_response('signup.html', {'title': _('Sign Up'), 'is_logged_in': is_logged_in},
                                      context_instance=RequestContext(request))
    else:
        return render_to_response('signup.html', {'title': _('Sign Up'), 'is_logged_in': is_logged_in},
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
                    l = Languages.get_language_by_user(user)
                    if l is None:
                        try:
                            lang = request.session['django_language']
                        except KeyError:
                            lang = 'en'
                            request.session['django_language'] = lang
                    else:
                        lang = l.language
                        request.session['django_language'] = lang

                    l = Languages(user=user, language=lang)
                    l.save()

                    if 'next' in request.POST:
                        nxt = request.POST['next']
                    return HttpResponseRedirect(nxt)
                else:
                    return render_to_response('message.html', {'title': _('Error!'), 'is_logged_in': is_logged_in,
                                                               'message': _('Account suspended!')},
                                              context_instance=RequestContext(request))
            else:
                return render_to_response('message.html', {'title': _('Error!'), 'is_logged_in': is_logged_in,
                                                           'message': _('Invalid credentials!')},
                                          context_instance=RequestContext(request))
        else:
            return render_to_response('auth.html', {'title': _('Login'), 'is_logged_in': is_logged_in,
                                                    'next': '/auctioneer/home/'},
                                      context_instance=RequestContext(request))
    else:
        if request.method == 'GET' and 'next' in request.GET:
            nxt = request.GET['next']

        return render_to_response('auth.html', {'title': _('Login'), 'is_logged_in': is_logged_in, 'next': nxt},
                                  context_instance=RequestContext(request))


def leave(request):
    logout(request)
    return HttpResponseRedirect('/auctioneer/home/')


def browse(request):
    is_logged_in = request.user.is_authenticated()
    if request.method == 'POST' and 'query' in request.POST:
        content = Auctions.get_by_query(request.POST['query'])
        return render_to_response('browse.html', {'title': _('Browse'), 'is_logged_in': is_logged_in, 'is_search': True,
                                                  'query': request.POST['query'], 'content_list': content},
                                  context_instance=RequestContext(request))
    else:
        content = Auctions.get_all()
        return render_to_response('browse.html', {'title': _('Browse'), 'is_logged_in': is_logged_in,
                                                  'is_search': False, 'content_list': content},
                                  context_instance=RequestContext(request))


@login_required
def account(request):
    is_logged_in = request.user.is_authenticated()
    user = request.user
    if request.method == 'POST' and 'email' in request.POST and 'password' in request.POST:
        user.email = request.POST['email']
        user.set_password(request.POST['password'])
        user.save()
        return render_to_response('message.html', {'title': _('Success!'), 'is_logged_in': is_logged_in,
                                                   'message': _('Account updated!')},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('account.html', {'title': _('Account'), 'is_logged_in': is_logged_in, 'user': user},
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
                return render_to_response('confirm.html', {'title': _('Confirmation'), 'is_logged_in': is_logged_in,
                                                           'auction_title': request.POST['title'],
                                                           'description': request.POST['description'],
                                                           'starting_price': request.POST['starting_price'],
                                                           'start': request.POST['start'],
                                                           'stop': request.POST['stop']
                                                           },
                                          context_instance=RequestContext(request))
            else:
                return render_to_response('create.html', {'title': _('Create auction'),
                                                          'is_logged_in': is_logged_in,
                                                          'message': _('Input error, try again!'),
                                                          },
                                          context_instance=RequestContext(request))
        except:
            return render_to_response('create.html', {'title': _('Create auction'),
                                                      'is_logged_in': is_logged_in,
                                                      'message': _('Input error, try again!'),
                                                      },
                                      context_instance=RequestContext(request))
    else:
        return render_to_response('create.html', {'title': _('Create auction'),
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
            send_mail(_('Auctioneer: Auction created!'), _('Your auction') + ' ' + new.title +
                      ' ' + _('was created successfully!'),
                      'auctioneer@some.mail', [new.seller.email], fail_silently=False)
            print 'Sent e-mail messages:'
            for message in mail.outbox:
                print message.subject
            return render_to_response('message.html', {'title': _('Success!'), 'is_logged_in': is_logged_in,
                                                       'message': _('Auction created!')},
                                      context_instance=RequestContext(request))
        else:
            session['valid'] = 'False'
            return render_to_response('message.html', {'title': _('Canceled!'), 'is_logged_in': is_logged_in,
                                                       'message': _('Auction creation was canceled!')},
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
    return render_to_response('main.html', {'title': _('My Auctions'), 'is_logged_in': is_logged_in,
                                            'tag': _('Auctions by')+' '+request.user.username, 'content_list': content},
                              context_instance=RequestContext(request))


def details(request, auction_id):
    auction = Auctions.get_by_id(auction_id)
    is_logged_in = request.user.is_authenticated()
    if is_logged_in and auction.seller == request.user:
        seller = True
    else:
        seller = False

    if auction is not None:
        return render_to_response('details.html', {'title': _('Details'), 'is_logged_in': is_logged_in,
                                                   'content': auction, 'seller': seller,
                                                   'admin': request.user.is_staff},
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('message.html', {'title': _('Not found!'), 'is_logged_in': is_logged_in,
                                                   'message': _('No such auction found!')},
                                  context_instance=RequestContext(request))


@login_required
def edit(request, auction_id):
    is_logged_in = request.user.is_authenticated()
    content = Auctions.get_by_id(auction_id)

    if content is not None:
        if request.user == content.seller:
            if request.method == 'POST' and 'description' in request.POST:
                content.description = request.POST['description']
                content.version += 1
                content.save()
                return HttpResponseRedirect('/auctioneer/auctions/' + str(content.id))
            else:
                return render_to_response('edit.html', {'title': _('Edit'), 'is_logged_in': is_logged_in,
                                                        'auction': content},
                                          context_instance=RequestContext(request))
        else:
            return render_to_response('message.html', {'title': _('Not authorized!'), 'is_logged_in': is_logged_in,
                                                       'message': _('Action not authorized!')},
                                      context_instance=RequestContext(request))
    else:
        return render_to_response('message.html', {'title': _('Not found!'), 'is_logged_in': is_logged_in,
                                                   'message': _('No such auction found!')},
                                  context_instance=RequestContext(request))


@login_required
def ban(request, auction_id):
    is_logged_in = request.user.is_authenticated()
    content = Auctions.get_by_id(auction_id)

    if content is not None:
        if request.user.has_perm('ban_auctions', Auctions):
            content.banned = True
            content.version += 1
            content.save()
            seller_message = (_('Auctioneer: Auction banned!'),
                              _('Your auction') + ' ' + content.title + ' ' + _('was banned!'),
                              'auctioneer@some.mail', [content.seller.email])
            bidders = []
            for bid in content.bids_set.all():
                bidders.append(bid.bidder.email)
            bidder_message = (_('Auctioneer: Auction banned!'),
                              _('The auction') + ' ' + content.title + ' ' + _('was banned!'),
                              'auctioneer@some.mail', bidders)
            send_mass_mail((seller_message, bidder_message))
            print 'Sent e-mail messages:'
            for message in mail.outbox:
                print message.subject

            return HttpResponseRedirect('/auctioneer/auctions/' + str(content.id))
        else:
            return render_to_response('message.html', {'title': _('Not authorized!'), 'is_logged_in': is_logged_in,
                                                       'message': _('Action not authorized!')},
                                      context_instance=RequestContext(request))
    else:
        return render_to_response('message.html', {'title': _('Not found!'), 'is_logged_in': is_logged_in,
                                                   'message': _('No such auction found!')},
                                  context_instance=RequestContext(request))


def language(request):
    is_logged_in = request.user.is_authenticated()

    if is_logged_in:
        user = request.user
        lang = Languages.get_language_by_user(user)
        if request.method == 'POST' and 'language' in request.POST:
            lang = Languages(user=user, language=request.POST['language'])
            lang.save()
            request.session['django_language'] = lang.language
            return HttpResponseRedirect('/auctioneer/home/')
        else:
            return render_to_response('language.html', {'title': _('Language'), 'is_logged_in': is_logged_in,
                                                        'language': lang.language},
                                      context_instance=RequestContext(request))
    else:
        if request.method == 'POST' and 'language' in request.POST:
            request.session['django_language'] = request.POST['language']
            return HttpResponseRedirect('/auctioneer/home/')
        else:
            return render_to_response('language.html', {'title': _('Language'), 'is_logged_in': is_logged_in,
                                                        'language': 'en'},
                                      context_instance=RequestContext(request))
