from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import datetime

# Create your models here.


class Auctions(models.Model):

    seller = models.ForeignKey(User)
    title = models.CharField(null=False, max_length=30)
    description = models.TextField(max_length=150)
    version = models.PositiveIntegerField(default=0)
    startingPrice = models.DecimalField(default=0.00, max_digits=12, decimal_places=2,
                                        validators=[MinValueValidator(Decimal('0.00'))])
    startDate = models.DateTimeField(null=False)
    stopDate = models.DateTimeField(null=False)
    banned = models.BooleanField(default=False)
    resolved = models.BooleanField(default=False)

    class Meta:
        permissions = (('ban_auctions', 'Can ban auctions'),)
        ordering = ['startDate']
        #order_with_respect_to = 'startDate'

    @classmethod
    def get_nearest(cls):
        try:
            return cls.objects.filter(banned=False, resolved=False, stopDate__gt=datetime.now()).order_by('stopDate')[:3]
        except:
            try:
                return cls.get_all()
            except:
                return None

    @classmethod
    def get_by_seller(cls, seller):
        try:
            return cls.objects.filter(seller=seller)
        except:
            return None

    @classmethod
    def get_by_id(cls, auction_id):
        try:
            return cls.objects.get(id=auction_id)
        except:
            return None

    @classmethod
    def get_by_query(cls, query):
        query = query.replace('\\', '\\\\')
        try:
            return cls.objects.filter(title__iregex=query, banned=False)
        except:
            return None

    @classmethod
    def get_all(cls):
        try:
            return cls.objects.all()
        except:
            return None

    @classmethod
    def get_active(cls):
        try:
            return cls.objects.filter(resolved=False, banned=False)
        except:
            return None


class Bids(models.Model):

    auction = models.ForeignKey(Auctions)
    bidder = models.ForeignKey(User)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    timestamp = models.DateTimeField()

    class Meta:
        ordering = ['-amount']
        #order_with_respect_to = 'auction'

    @classmethod
    def get_by_auction_all(cls, auction):
        try:
            return cls.objects.filter(auction=auction)
        except:
            return None

    @classmethod
    def get_by_auction_highest(cls, auction):
        try:
            return cls.objects.filter(auction=auction)[1]
        except:
            return None


class Languages(models.Model):

    user = models.ForeignKey(User, primary_key=True)
    language = models.CharField(max_length=10, default='en')

    @classmethod
    def get_language_by_user(cls, user):
        try:
            return cls.objects.get(user=user)
        except:
            return None
