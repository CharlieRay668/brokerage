from django import forms
import datetime as dt
from .models import Trade, EquityPosition, OptionPosition


class CreateNewEquityPosition(forms.ModelForm):
    #symbol = forms.CharField(max_length=30)
    quantity = forms.IntegerField()
    action = forms.ChoiceField(label = "Action", choices=[(1, "Buy"),
                                                        (2, "Sell"),
                                                        (3, "Buy to Cover"),
                                                        (4, "Sell Short")])
    order_type = forms.ChoiceField(label = "Type", choices=[(1, "Limit"),
                                                            (2, "Market"),
                                                            (3, "Stop Market"),
                                                            (4, "Stop Limit"),
                                                            (5, "Trailing Stop %"),
                                                            (6, "Traling Stop $")])
    order_expiration = forms.ChoiceField(label = "Order Expiration", choices=[(1, "Day"),(2, "GTC")])
    limit_price = forms.IntegerField(required=False)
    class Meta:
        model = EquityPosition
        fields = ['quantity', 'action', 'order_type', 'limit_price','order_expiration']