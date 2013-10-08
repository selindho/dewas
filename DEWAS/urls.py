from django.conf.urls import patterns, include, url
from Auctioneer.views import *
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

    url(r'^auctioneer/home/$', home),
    # url(r'^auctioneer/search/(?P<query>\w+)/$', search),
    url(r'^auctioneer/signup/$', sign_up),
    # url(r'^auctioneer/account/edit/$', edit_account),
    # url(r'^auctioneer/login/$', login),
    # url(r'^auctioneer/logout/$', logout),
    # url(r'^auctioneer/auction/(?P<id>\w+)/$', show_auction),
    # url(r'^auctioneer/auction/create/$', create_auction),
    # url(r'^auctioneer/auction/(?P<id>\w+)/cancel/$', cancel_auction),
    # url(r'^auctioneer/auction/(?P<id>\w+)/bid/$', bid)

)
