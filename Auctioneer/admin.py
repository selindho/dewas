from django.contrib import admin
from Auctioneer.models import *


class AuctionsAdmin(admin.ModelAdmin):
    pass


class BidsAdmin(admin.ModelAdmin):
    pass


admin.site.register(Auctions)
admin.site.register(Bids)