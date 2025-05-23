from django.contrib import admin
from .models import Currency, MiningPlan, User, TradingPlan,Deposite,CopiedTrade,ContractPaymentMethod, TakeTrade, Withdrawal

# Register your models here.

admin.site.register(User)
admin.site.register(TradingPlan)
admin.site.register(Deposite)
admin.site.register(Currency)
admin.site.register(MiningPlan)
admin.site.register(CopiedTrade)
admin.site.register(ContractPaymentMethod)
admin.site.register(TakeTrade)
admin.site.register(Withdrawal)