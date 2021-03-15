from django import forms
import datetime as dt
from .models import Account

class CreateAccount(forms.ModelForm):
    #symbol = forms.CharField(max_length=30)
    name = forms.CharField(max_length=20, label="Account Name")
    cash_amount = forms.FloatField(label="Initial Account Balance")
    class Meta:
        model = Account
        fields = ['name', 'cash_amount']