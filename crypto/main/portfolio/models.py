from django.db import models
from django.contrib.auth.models import User


class CoinList(models.Model):
    currency_id = models.CharField(max_length=100)
    symbol = models.CharField(max_length=100)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coins = models.ManyToManyField(CoinList)

    def __str__(self):
        return self.user.username
