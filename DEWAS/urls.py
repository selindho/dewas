from django.conf.urls import patterns, include, url
from Auctioneer.views import *
from Auctioneer.rest_views import *
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'DEWAS.views.home', name='home'),
    # url(r'^DEWAS/', include('DEWAS.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # Main UI
    url(r'^auctioneer/$', home),
    url(r'^auctioneer/home/$', home),
    url(r'^auctioneer/auctions/$', browse),
    url(r'^auctioneer/signup/$', sign_up),
    url(r'^auctioneer/account/$', account),
    url(r'^auctioneer/account/auctions/$', auctions),
    url(r'^auctioneer/login/$', auth),
    url(r'^auctioneer/logout/$', leave),
    url(r'^auctioneer/auctions/(?P<auction_id>\d+)/$', details),
    url(r'^auctioneer/auctions/create/$', create),
    url(r'^auctioneer/auctions/confirm/$', confirm),
    url(r'^auctioneer/auctions/(?P<auction_id>\w+)/edit/$', edit),
    url(r'^auctioneer/auctions/(?P<auction_id>\w+)/ban/$', ban),
    # url(r'^auctioneer/auctions/(?P<auction_id>\w+)/bid/$', bid)

    # RESTful interface
    url(r'^auctioneer/api/auctions/(?P<query>\w+)?$', rest_auctions)

)
