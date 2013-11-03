from django_cron import CronJobBase, Schedule
from django.shortcuts import get_list_or_404
from django.core.mail import send_mass_mail
from Auctioneer.models import *


class AuctionResolver(CronJobBase):
    RUN_EVERY_MINS = 1
    RETRY_AFTER_FAILURE_MINS = 1
    MIN_NUM_FAILURES = 5

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = 'Auctioneer.auction_resolver'

    def do(self):
        auctions = get_list_or_404(Auctions, banned=False, resolved=False)

        now = datetime.now()
        for auction in auctions:
            print auction.title
            if auction.stopDate < now:
                print auction.stopDate

                bids = get_list_or_404(auction.bids_set.all())

                seller_message = ('Auctioneer: Auction resolved!',
                                  'Your auction ' + auction.title + ' was resolved!',
                                  'auctioneer@some.mail', [auction.seller.email])

                bidders = []
                for bid in bids:
                    bidders.append(bid.bidder.email)

                bidder_message = ('Auctioneer: Auction resolved!',
                                  'The auction ' + auction.title + ' was resolved!',
                                  'auctioneer@some.mail', bidders)

                winner = Bids.get_by_auction_highest(auction)

                winner_message = ('Auctioneer: Auction won!',
                                  'You won the auction ' + auction.title + '!',
                                  'auctioneer@some.mail', winner.bidder.email)
                send_mass_mail((seller_message, bidder_message, winner_message))

                auction.resolved = True
                auction.save()