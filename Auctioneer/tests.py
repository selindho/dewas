from django.test import TestCase
from datetime import timedelta
from Auctioneer.models import *
from django.core import mail
from django.test import Client


class AuctionCreationTest(TestCase):

    def setUp(self):
        User.objects.create_user('smith', 'smith@domain.com', 'pass')
        self.client.login(username='smith', password='pass')

    def test_valid_confirm(self):
        start = datetime.now()
        stop = start + timedelta(days=3)
        pre_count = Auctions.objects.count()

        response = self.client.post(path='/auctioneer/auctions/create/', data={'title': 'Title',
                                                                               'description': 'Description',
                                                                               'start': start,
                                                                               'stop': stop,
                                                                               'starting_price': 100})
        self.assertEqual(response.status_code, 200)

        session = self.client.session
        session['valid'] = 'True'
        session['title'] = 'Title'
        session['description'] = 'Description'
        session['start'] = start
        session['stop'] = stop
        session['starting_price'] = 100
        session.save()

        response = self.client.post(path='/auctioneer/auctions/confirm/', data={'status': 'True'})

        self.assertEqual(response.status_code, 200)

        post_count = Auctions.objects.count()

        # Check whether auction was created
        self.assertEqual(pre_count+1, post_count)

        # Check whether email was sent
        self.assertEqual(len(mail.outbox), 1)

    def test_valid_no_confirm(self):
        start = datetime.now()
        stop = start + timedelta(days=3)
        pre_count = Auctions.objects.count()

        response = self.client.post(path='/auctioneer/auctions/create/', data={'title': 'Title',
                                                                               'description': 'Description',
                                                                               'start': start,
                                                                               'stop': stop,
                                                                               'starting_price': 100})
        self.assertEqual(response.status_code, 200)

        session = self.client.session
        session['valid'] = 'True'
        session['title'] = 'Title'
        session['description'] = 'Description'
        session['start'] = start
        session['stop'] = stop
        session['starting_price'] = 100
        session.save()

        response = self.client.post(path='/auctioneer/auctions/confirm/', data={'status': 'False'})

        self.assertEqual(response.status_code, 200)

        post_count = Auctions.objects.count()

        # Check whether auction was created
        self.assertEqual(pre_count, post_count)

        # Check whether email was sent
        self.assertEqual(len(mail.outbox), 0)

    def test_invalid_duration(self):
        start = datetime.now()
        stop = start + timedelta(days=2)
        pre_count = Auctions.objects.count()

        response = self.client.post(path='/auctioneer/auctions/create/', data={'title': 'Title',
                                                                               'description': 'Description',
                                                                               'start': start,
                                                                               'stop': stop,
                                                                               'starting_price': 100})
        self.assertEqual(response.status_code, 200)

        session = self.client.session
        session['valid'] = 'False'
        session['title'] = 'Title'
        session['description'] = 'Description'
        session['start'] = start
        session['stop'] = stop
        session['starting_price'] = 100
        session.save()

        response = self.client.post(path='/auctioneer/auctions/confirm/', data={'status': 'True'})

        self.assertEqual(response.status_code, 200)

        post_count = Auctions.objects.count()

        # Check whether auction was created
        self.assertEqual(pre_count, post_count)

        # Check whether email was sent
        self.assertEqual(len(mail.outbox), 0)


class BidTestCase(TestCase):

    def setUp(self):
        User.objects.create_user('smith', 'smith@domain.com', 'pass')
        self.client.login(username='smith', password='pass')

    def test_place_low_initial_bid(self):
        john = User.objects.create_user('john', 'john@domain.com', 'pass')
        auction = Auctions(seller=john, title='stuff', description='cool stuff', startingPrice=Decimal('5.00'),
                           startDate='2012-12-24 00:00', stopDate='2020-12-24 00:00')
        auction.save()

        response = self.client.get('/auctioneer/auctions/' + str(auction.id) + '/bid/')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(auction.bids_set.count(), 0)
        self.client.post('/auctioneer/auctions/' + str(auction.id) + '/bid/', data={'amount': '0'})
        self.assertEqual(auction.bids_set.count(), 0)

    def test_place_high_initial_bid(self):
        john = User.objects.create_user('john', 'john@domain.com', 'pass')
        auction = Auctions(seller=john, title='stuff', description='cool stuff', startingPrice=Decimal('5.00'),
                           startDate='2012-12-24 00:00', stopDate='2020-12-24 00:00')
        auction.save()

        response = self.client.get('/auctioneer/auctions/' + str(auction.id) + '/bid/')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(auction.bids_set.count(), 0)
        self.client.post('/auctioneer/auctions/' + str(auction.id) + '/bid/', data={'amount': '10.00'})
        self.assertEqual(auction.bids_set.count(), 1)

    def test_place_low_counter_bid(self):
        john = User.objects.create_user('john', 'john@domain.com', 'pass')
        sam = User.objects.create_user('sam', 'john@domain.com', 'pass')
        auction = Auctions(seller=john, title='stuff', description='cool stuff', startingPrice=Decimal('5.00'),
                           startDate='2012-12-24 00:00', stopDate='2020-12-24 00:00')
        auction.save()
        bid = Bids(auction=auction, bidder=sam, amount=10, timestamp=datetime.now())
        bid.save()

        response = self.client.get('/auctioneer/auctions/' + str(auction.id) + '/bid/')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(auction.bids_set.count(), 1)
        self.client.post('/auctioneer/auctions/' + str(auction.id) + '/bid/', data={'amount': '7'})
        self.assertEqual(auction.bids_set.count(), 1)

    def test_place_high_counter_bid(self):
        john = User.objects.create_user('john', 'john@domain.com', 'pass')
        sam = User.objects.create_user('sam', 'john@domain.com', 'pass')
        auction = Auctions(seller=john, title='stuff', description='cool stuff', startingPrice=Decimal('5.00'),
                           startDate='2012-12-24 00:00', stopDate='2020-12-24 00:00')
        auction.save()
        bid = Bids(auction=auction, bidder=sam, amount=10, timestamp=datetime.now())
        bid.save()

        response = self.client.get('/auctioneer/auctions/' + str(auction.id) + '/bid/')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(auction.bids_set.count(), 1)
        self.client.post('/auctioneer/auctions/' + str(auction.id) + '/bid/', data={'amount': '15'})
        self.assertEqual(auction.bids_set.count(), 2)

    def test_place_own_auction_bid(self):
        self.client.logout()
        john = User.objects.create_user('john', 'john@domain.com', 'pass')
        self.client.login(username='john', password='pass')
        auction = Auctions(seller=john, title='stuff', description='cool stuff', startingPrice=Decimal('5.00'),
                           startDate='2012-12-24 00:00', stopDate='2020-12-24 00:00')
        auction.save()

        response = self.client.get('/auctioneer/auctions/' + str(auction.id) + '/bid/')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(auction.bids_set.count(), 0)
        self.client.post('/auctioneer/auctions/' + str(auction.id) + '/bid/', data={'amount': '15'})
        self.assertEqual(auction.bids_set.count(), 0)

    def test_place_own_counter_bid(self):
        john = User.objects.create_user('john', 'john@domain.com', 'pass')
        auction = Auctions(seller=john, title='stuff', description='cool stuff', startingPrice=Decimal('5.00'),
                           startDate='2012-12-24 00:00', stopDate='2020-12-24 00:00')
        auction.save()

        response = self.client.get('/auctioneer/auctions/' + str(auction.id) + '/bid/')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(auction.bids_set.count(), 0)
        self.client.post('/auctioneer/auctions/' + str(auction.id) + '/bid/', data={'amount': '15'})
        self.assertEqual(auction.bids_set.count(), 1)
        self.client.post('/auctioneer/auctions/' + str(auction.id) + '/bid/', data={'amount': '20'})
        self.assertEqual(auction.bids_set.count(), 1)

    def test_place_concurrent_bid(self):
        john = User.objects.create_user('john', 'john@domain.com', 'pass')
        auction = Auctions(seller=john, title='stuff', description='cool stuff', startingPrice=Decimal('5.00'),
                           startDate='2012-12-24 00:00', stopDate='2020-12-24 00:00')
        auction.save()

        self.assertEqual(auction.bids_set.count(), 0)
        response = self.client.get('/auctioneer/auctions/' + str(auction.id) + '/bid/')
        self.assertEqual(response.status_code, 200)

        # Somebody alters the auction..
        auction.version = int(auction.version) + 1
        auction.save()

        self.client.post('/auctioneer/auctions/' + str(auction.id) + '/bid/', data={'amount': '15'})
        self.assertEqual(auction.bids_set.count(), 0)

    def test_place_bid_versioning(self):
        john = User.objects.create_user('john', 'john@domain.com', 'pass')
        auction = Auctions(seller=john, title='stuff', description='cool stuff', startingPrice=Decimal('5.00'),
                           startDate='2012-12-24 00:00', stopDate='2020-12-24 00:00')
        auction.save()

        self.assertEqual(auction.bids_set.count(), 0)
        self.assertEqual(Auctions.get_by_id(auction.id).version, 0)
        response = self.client.get('/auctioneer/auctions/' + str(auction.id) + '/bid/')
        self.assertEqual(response.status_code, 200)

        self.client.post('/auctioneer/auctions/' + str(auction.id) + '/bid/', data={'amount': '15'})
        self.assertEqual(auction.bids_set.count(), 1)
        self.assertEqual(Auctions.get_by_id(auction.id).version, 1)