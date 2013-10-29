"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase, Client


class AuctionCreationTest(TestCase):
    def test_basic_addition(self):
        # Pre
        client = Client()
        client.login(username='admin', password='admin')



