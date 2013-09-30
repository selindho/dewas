from django.db import models

# Create your models here.


class Auctions(models.Model):
    owner = models.CharField(null=False, max_length=30)
    title = models.CharField(max_length=30)
    startingPrice = models.FloatField(null=True)
    buyoutPrice = models.FloatField(null=True)
    startDate = models.DateTimeField()
    stopDate = models.DateTimeField()

    @classmethod
    def get_latest(cls):
        try:
            return cls.objects.latest('startDate')[:5]
        except:
            return None

    @classmethod
    def get_by_owner(cls, id):
        return cls.objects.all().filter(owner=id)

    @classmethod
    def get_by_id(cls, id):
        return cls.objects.get(id=id)


class Accounts(models.Model):
    username = models.CharField(null=False, max_length=30, primary_key=True, unique=True)
    firstName = models.CharField(max_length=30)
    lastName = models.CharField(max_length=30)
    password = models.CharField(null=False, max_length=30)


class Bids(models.Model):
    auction = models.PositiveIntegerField(null=False)
    owner = models.CharField(null=False, max_length=30)
    amount = models.DecimalField(null=False, max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(null=False)


