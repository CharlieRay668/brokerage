from django.db import models
from django.conf import settings
import datetime as dt
from trade_accounts.models import Account
# Create your models here.

class Position(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="positions", null=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name = "acct_positions", null=True)
    position_id = models.TextField(default=None)
    symbol = models.CharField(max_length=30)
    quantity = models.IntegerField(default=None)
    fill_price = models.FloatField(default=-999, editable=False)
    position_info = models.JSONField(default=None)
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
    order_action = models.IntegerField(choices=action_choices, default=1, editable=False)
    order_type = models.IntegerField(choices=order_type_choices, default=2)
    order_expiration = models.IntegerField(choices=order_expiration_choices, default='1')
    order_execution_date = models.DateTimeField(default=None)
    limit_price = models.IntegerField(default=None)


## class Order(models.Model):
#     linking_position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name="orders", null=True)
#     #[TSLA, Limit, Day, 30 690, False, 2021/1/10 14:24:23
#     order_type_choices = (
#         (1, "Limit"),
#         (2, "Market"),
#         (3, "Stop Market"),
#         (4, "Stop Limit"),
#         (5, "Trailing Stop %"),
#         (6, "Traling Stop $"))
#     order_type = models.IntegerField(choices=order_type_choices)
#     order_expiration_choices = (
#         (1, "Day"),
#         (2, "GTC"))
#     order_expiration = models.IntegerField(choices=order_expiration_choices)
#     order_quantity = models.IntegerField()
#     order_fill_price = models.IntegerField()
#     order_fill_happen = models.BooleanField()
#     order_execution_datetime = models.DateTimeField()

# class Trade(models.Model):
#     trader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trades", null=True)

# class OptionPosition(models.Model):
#     parent_trade = models.ForeignKey(Trade, on_delete=models.CASCADE, related_name="option_positions", null=True)
#     symbol = models.CharField(max_length=30)
#     quantity = models.IntegerField()
#     action_choices = (
#         (1, "Buy"),
#         (2, "Sell"),
#         (3, "Buy to Cover"),
#         (4, "Sell Short"))
#     order_type_choices = (
#         (1, "Limit"),
#         (2, "Market"),
#         (3, "Stop Market"),
#         (4, "Stop Limit"),
#         (5, "Trailing Stop %"),
#         (6, "Traling Stop $"))
#     order_expiration_choices = (
#         (1, "Day"),
#         (2, "GTC"))
#     action = models.IntegerField(choices=action_choices)
#     order_type = models.IntegerField(choices=order_type_choices)
#     order_expiration = models.IntegerField(choices=order_expiration_choices)
#     order_execution_date = models.DateTimeField()
#     fill_price = models.IntegerField(null=True)
#     limit_price = models.IntegerField(null=True)

# class EquityPosition(models.Model):
#     parent_trade = models.ForeignKey(Trade, on_delete=models.CASCADE, related_name="equity_positions", null=True)
#     symbol = models.CharField(max_length=30)
#     quantity = models.IntegerField()
#     action_choices = (
#         (1, "Buy"),
#         (2, "Sell"),
#         (3, "Buy to Cover"),
#         (4, "Sell Short"))
#     order_type_choices = (
#         (1, "Limit"),
#         (2, "Market"),
#         (3, "Stop Market"),
#         (4, "Stop Limit"),
#         (5, "Trailing Stop %"),
#         (6, "Traling Stop $"))
#     order_expiration_choices = (
#         (1, "Day"),
#         (2, "GTC"))
#     action = models.IntegerField(choices=action_choices)
#     order_type = models.IntegerField(choices=order_type_choices)
#     order_expiration = models.IntegerField(choices=order_expiration_choices)
#     order_execution_date = models.DateTimeField()
#     fill_price = models.IntegerField(null=True)
#     limit_price = models.IntegerField(null=True)