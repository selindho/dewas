from django.db import models

# Create your models here.


class Auctions(models.Model):
    owner = models.CharField(null=False, max_length=30)
    title = models.CharField(max_length=30)
    version = models.PositiveIntegerField(default=0)
    startingPrice = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    startDate = models.DateTimeField()
    stopDate = models.DateTimeField()

    @classmethod
    def get_latest(cls):
        try:
            return cls.objects.latest('startDate')[:5]
        except:
            return None

    @classmethod
    def get_by_owner(cls, owner):
        return cls.objects.all().filter(owner=owner)

    @classmethod
    def get_by_id(cls, id):
        return cls.objects.get(id=id)


class Bids(models.Model):
    auction = models.ForeignKey(Auctions)
    owner = models.CharField(max_length=30)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField()

    @classmethod
    def get_by_auction(cls, auction):
        return cls.objects.all().filter(auction=auction)


