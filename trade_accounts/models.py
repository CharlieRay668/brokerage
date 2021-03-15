from django.db import models
from django.conf import settings
import datetime as dt
# Create your models here.

class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="accounts", null=False)
    name = models.TextField(max_length=20, null=False)
    cash_amount = models.FloatField()
    equity_amount = models.FloatField()
    option_amount = models.FloatField()
    short_equity_amount = models.FloatField()
    short_option_amount = models.FloatField()