from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


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


class PortfolioCoin(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    coin = models.ForeignKey(CoinList, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=8, default=0)  # Количество монет
    price = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)


class PortfolioHistory(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    total_value = models.DecimalField(max_digits=20, decimal_places=4)
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.portfolio.user.username} - {self.timestamp}"


class Coin(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Название монеты
    symbol = models.CharField(max_length=10, unique=True)  # Символ монеты (например, BTC)
    price = models.FloatField()  # Текущая цена монеты (в USD)

    def __str__(self):
        return self.name
