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
        content = Auctions.get_active()
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
            now = datetime.now()
            if request.POST['start'] != 'now':
                start = datetime.strptime(request.POST['start'], '%Y-%m-%d %H:%M')
            else:
                start = datetime.now()
            stop = datetime.strptime(request.POST['stop'], '%Y-%m-%d %H:%M')
            exp = re.compile(r'^\d{1,10}(.\d{0,2})?$')
            result = exp.match(request.POST['starting_price'])
            if stop >= start + timedelta(days=3) and (request.POST['start'] == 'now' or start >= now) and result is not None:
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
            send_mail('Auctioneer: Auction created!', 'Your auction' + ' ' + new.title +
                      ' ' + 'was created successfully!',
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
        if request.POST['start'] == 'now':
            request.session['start'] = datetime.now()
        else:
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
            seller_message = ('Auctioneer: Auction banned!',
                              'Your auction' + ' ' + content.title + ' ' + 'was banned!',
                              'auctioneer@some.mail', [content.seller.email])
            bidders = []
            for b in content.bids_set.all():
                bidders.append(b.bidder.email)
            bidder_message = ('Auctioneer: Auction banned!',
                              'The auction' + ' ' + content.title + ' ' + 'was banned!',
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


@login_required
def bid(request, auction_id):
    is_logged_in = request.user.is_authenticated()
    user = request.user
    auction = Auctions.get_by_id(auction_id)

    if request.method == 'POST' and 'amount' in request.POST and 'version' in request.session:
        status = bid_validate(user, auction, request.session['version'], request.POST['amount'])

        if status == 'valid':
            auction.version = int(auction.version) + 1
            b = Bids(auction=auction, bidder=user, amount=request.POST['amount'], timestamp=datetime.now())
            auction.save()
            b.save()
            bid_send_mail(user, auction)

            return HttpResponseRedirect('/auctioneer/auctions/'+auction_id+'/')

        elif status == 'invalid bid':

            return render_to_response('message.html', {'title': _('Invalid bid!'),
                                      'is_logged_in': is_logged_in,
                                      'message': _('Your bid is invalid!')},
                                      context_instance=RequestContext(request))

        elif status == 'already top':

            return render_to_response('message.html', {'title': _('Already high bidder!'),
                                      'is_logged_in': is_logged_in,
                                      'message': _('You are already the high bidder!')},
                                      context_instance=RequestContext(request))

        elif status == 'invalid version':

            return render_to_response('bid.html', {'title': _('Bid'), 'is_logged_in': is_logged_in,
                                      'auction': auction,
                                      'message': _('Auction has changed!')},
                                      context_instance=RequestContext(request))

        elif status == 'own auction':

            return render_to_response('message.html', {'title': _('Not Allowed!'), 'is_logged_in': is_logged_in,
                                      'message': _('Cannot bid on your own auction!')},
                                      context_instance=RequestContext(request))

        elif status == 'invalid auction':

            return render_to_response('message.html', {'title': _('Not found!'), 'is_logged_in': is_logged_in,
                                      'message': _('No such auction found!')},
                                      context_instance=RequestContext(request))

        elif status == 'auction resolved':

            return render_to_response('message.html', {'title': _('Auction resolved!'), 'is_logged_in': is_logged_in,
                                      'message': _('Auction is already resolved!')},
                                      context_instance=RequestContext(request))

        elif status == 'auction not started':

            return render_to_response('message.html', {'title': _('Auction not started!'), 'is_logged_in': is_logged_in,
                                      'message': _('Auction has not started yet!')},
                                      context_instance=RequestContext(request))

        else:
            return HttpResponseRedirect('/auctioneer/auctions/'+auction_id+'/')

    else:
        request.session['version'] = auction.version
        return render_to_response('bid.html', {'title': _('Bid'), 'is_logged_in': is_logged_in,
                                  'auction': auction},
                                  context_instance=RequestContext(request))


def bid_send_mail(user, auction):
    seller_message = ('Auctioneer: Bid accepted!!',
                      user.username + ' has bid on your auction ' + auction.title + '.',
                      'auctioneer@some.mail', [auction.seller.email])
    top_bidder_message = ('Auctioneer: Bid accepted!!',
                          'Your bid on ' + auction.title + ' has been accepted.',
                          'auctioneer@some.mail', [user.email])
    send_mass_mail((seller_message, top_bidder_message))

    bidders = []
    for b in list(auction.bids_set.all()):
        if b.bidder != user:
            bidders.append(b.bidder.email)
        if len(bidders) > 0:
            bidder_message = ('Auctioneer: You were outbid!',
                              'Someone outbid you on the auction ' + auction.title + '!',
                              'auctioneer@some.mail', bidders)
            send_mass_mail((bidder_message,))


def bid_validate(user, auction, version, amount):
    if auction is not None and not auction.banned:
        if auction.startDate <= datetime.now():
            if not auction.resolved:
                if user != auction.seller:
                    if version == auction.version:
                        top = list(auction.bids_set.all()[:1])
                        exp = re.compile(r'^\d{1,10}(.\d{0,2})?$')
                        result = exp.match(amount)
                        amount = Decimal(amount)
                        if top:
                            if top[0].bidder != user:
                                if result is not None and amount >= top[0].amount + Decimal('0.01'):
                                    return "valid"
                                else:
                                    return "invalid bid"
                            else:
                                return "already top"
                        else:
                            if result is not None and amount >= auction.startingPrice + Decimal('0.01'):
                                return "valid"
                            else:
                                return "invalid bid"
                    else:
                        return "invalid version"
                else:
                    return "own auction"
            else:
                return "auction resolved"
        else:
            return "auction not started"
    return "invalid auction"