from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.


class Auctions(models.Model):

    seller = models.CharField(null=False, max_length=30)
    title = models.CharField(null=False, max_length=30)
    description = models.TextField(max_length=150)
    version = models.PositiveIntegerField(default=0)
    startingPrice = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, validators=[MinValueValidator(0.00)])
    startDate = models.DateTimeField(null=False)
    stopDate = models.DateTimeField(null=False)
    banned = models.BooleanField(default=False)
    resolved = models.BooleanField(default=False)

    class Meta:
        permissions = (('ban_auctions', 'Can ban auctions.'),)
        ordering = ['startDate']
        #order_with_respect_to = 'startDate'

    @classmethod
    def get_latest(cls):
        try:
            return cls.objects.filter(banned=False, resolved=False).order_by('startDate')[:5]
        except:
            try:
                return cls.get_all()
            except:
                return None

    @property
    def has_bids(self):
        if self.objects.select_related('bids_set').all().count() > 0:
            return True
        else:
            return False

    @classmethod
    def get_by_seller(cls, seller):
        try:
            return cls.objects.filter(seller=seller, banned=False)
        except:
            return None

    @classmethod
    def get_by_id(cls, id):
        try:
            return cls.objects.get(id=id).filter(banned=False)
        except:
            return None

    @classmethod
    def get_by_query(cls, query):
        query = query.replace('\\', '\\\\')
        try:
            return cls.objects.filter(title__iregex=query)
        except:
            return None

    @classmethod
    def get_all(cls):
        try:
            return cls.objects.all()
        except:
            return None


class Bids(models.Model):

    auction = models.ForeignKey(Auctions)
    owner = models.CharField(max_length=30)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.00)])
    timestamp = models.DateTimeField()

    class Meta:
        ordering = ['-timestamp']
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
            return cls.objects.filter(auction=auction)
        except:
            return None