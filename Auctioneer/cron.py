from django_cron import CronJobBase, Schedule
from django.core.mail import send_mass_mail
from Auctioneer.models import *


class AuctionResolver(CronJobBase):
    RUN_EVERY_MINS = 1
    RETRY_AFTER_FAILURE_MINS = 1
    MIN_NUM_FAILURES = 5

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = 'Auctioneer.auction_resolver'

    def do(self):
        auctions = Auctions.objects.filter(banned=False, resolved=False)

        now = datetime.now()
        if auctions is not None:
            for auction in auctions:
                if auction.stopDate < now:
                    seller_message = ('Auctioneer: Auction resolved!',
                                      'Your auction ' + auction.title + ' was resolved!',
                                      'auctioneer@some.mail', [auction.seller.email])
                    send_mass_mail((seller_message,))

                    bids = list(auction.bids_set.all())
                    bidders = []
                    winner = None
                    if bids:
                        for bid in bids:
                            bidders.append(bid.bidder.email)

                        bidder_message = ('Auctioneer: Auction resolved!',
                                          'The auction ' + auction.title + ' was resolved!',
                                          'auctioneer@some.mail', bidders)
                        send_mass_mail((bidder_message,))

                        winner = bids[0]
                        winner_message = ('Auctioneer: Auction won!',
                                          'You won the auction ' + auction.title + '!',
                                          'auctioneer@some.mail', [winner.bidder.email])
                        send_mass_mail((winner_message,))

                    auction.resolved = True
                    auction.save()

                    if winner is not None:
                        print auction.title + '@' + str(auction.stopDate) + ': ' + str(winner.bidder) + '$' + str(winner.amount)
                    else:
                        print auction.title + '@' + str(auction.stopDate) + ': No bids.'

        print 'Cron job executed!'