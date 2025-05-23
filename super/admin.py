from django.contrib import admin
from .models import Role, Trader, Coin, NewCoin, Contact, Currency, Crypto, Forex, StockList

# Register your models here.

admin.site.register(Role)
admin.site.register(Trader)
admin.site.register(Coin)
admin.site.register(NewCoin)
admin.site.register(Contact)
admin.site.register(Currency)
admin.site.register(Crypto)
admin.site.register(Forex)
admin.site.register(StockList)