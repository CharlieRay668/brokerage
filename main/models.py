from django.db import models
from django.conf import settings

# Create your models here.

class Trade(models.Model):
    trader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trades", null=True)

class OptionPosition(models.Model):
    parent_trade = models.ForeignKey(Trade, on_delete=models.CASCADE, related_name="option_positions", null=True)
    symbol = models.CharField(max_length=30)
    quantity = models.IntegerField()
    action_choices = (
        (1, "Buy"),
        (2, "Sell"),
        (3, "Buy to Cover"),
        (4, "Sell Short"))
    order_type_choices = (
        (1, "Limit"),
        (2, "Market"),
        (3, "Stop Market"),
        (4, "Stop Limit"),
        (5, "Trailing Stop %"),
        (6, "Traling Stop $"))
    order_expiration_choices = (
        (1, "Day"),
        (2, "GTC"))
    action = models.IntegerField(choices=action_choices)
    order_type = models.IntegerField(choices=order_type_choices)
    order_expiration = models.IntegerField(choices=order_expiration_choices)
    order_execution_date = models.DateTimeField()
    fill_price = models.IntegerField(null=True)
    limit_price = models.IntegerField(null=True)

class EquityPosition(models.Model):
    parent_trade = models.ForeignKey(Trade, on_delete=models.CASCADE, related_name="equity_positions", null=True)
    symbol = models.CharField(max_length=30)
    quantity = models.IntegerField()
    action_choices = (
        (1, "Buy"),
        (2, "Sell"),
        (3, "Buy to Cover"),
        (4, "Sell Short"))
    order_type_choices = (
        (1, "Limit"),
        (2, "Market"),
        (3, "Stop Market"),
        (4, "Stop Limit"),
        (5, "Trailing Stop %"),
        (6, "Traling Stop $"))
    order_expiration_choices = (
        (1, "Day"),
        (2, "GTC"))
    action = models.IntegerField(choices=action_choices)
    order_type = models.IntegerField(choices=order_type_choices)
    order_expiration = models.IntegerField(choices=order_expiration_choices)
    order_execution_date = models.DateTimeField()
    fill_price = models.IntegerField(null=True)
    limit_price = models.IntegerField(null=True)