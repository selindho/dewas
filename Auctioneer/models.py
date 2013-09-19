from django.db import models

# Create your models here.

class Auctions(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    owner = models.CharField(max_length=30)
    title = models.CharField(max_length=30)
    startingPrice = models.FloatField(null=True)
    buyoutPrice = models.FloatField(null=True)
    startDate = models.DateTimeField()
    stopDate = models.DateTimeField()

class Accounts(models.Model):
    username = models.CharField(max_length=30, primary_key=True)
    firstName = models.CharField(max_length=30)
    lastName = models.CharField(max_length=30)
    password = models.CharField(max_length=30)

