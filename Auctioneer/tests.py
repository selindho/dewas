from django.test import TestCase
from datetime import timedelta
from Auctioneer.models import *
from django.core import mail


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