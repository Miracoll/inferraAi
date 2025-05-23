from django import forms
from .models import Trader
from account.models import Currency

class CreateTraderForm(forms.ModelForm):
    class Meta:
        model = Trader
        fields = ['name','win_rate','profit','image','followers']
        
class CurrencyForm(forms.ModelForm):
    class Meta:
        model = Currency
        fields = ['abbr','currency','address']