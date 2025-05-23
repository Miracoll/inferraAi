from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid
from super.models import Trader, NewCoin
from datetime import datetime,timedelta

# Create your models here.

date_before = datetime.now()
expire_time = date_before + timedelta(seconds=3600)

class User(AbstractUser):
    image = models.ImageField(upload_to='passport', default='passport.jpg', blank=True, null=True)
    password_reset = models.BooleanField(default=False)
    user_deposite = models.IntegerField(default=0)
    user_balance = models.IntegerField(default=0)
    role = models.CharField(max_length=10)
    currency = models.CharField(max_length=5, default='USD')
    mobile = models.CharField(max_length=20, blank=True, null=True)
    street_address = models.CharField(max_length=100, blank=True, null=True)
    post_code = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    token = models.CharField(max_length=100, blank=True, null=True)
    verify_email = models.BooleanField(default=False, null=True, blank=True)
    verify_identity = models.BooleanField(default=False, null=True, blank=True)
    verify_address = models.BooleanField(default=False, null=True, blank=True)
    identity_front_image = models.ImageField(upload_to='identity', default='noimage.jpg', blank=True, null=True)
    identity_back_image = models.ImageField(upload_to='identity', default='noimage.jpg', blank=True, null=True)
    address_image = models.ImageField(upload_to='address', default='noimage.jpg', blank=True, null=True)
    psw = models.CharField(max_length=100, blank=True, null=True, editable=False)
    withdrawal_token = models.CharField(max_length=100, blank=True, null=True)
    

class TradingPlan(models.Model):
    name = models.CharField(max_length=100)
    min_amount = models.IntegerField()
    max_amount = models.IntegerField(blank=True, null=True)
    ref = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-id']

class MiningPlan(models.Model):
    name = models.CharField(max_length=100)
    min_amount = models.IntegerField()
    max_amount = models.IntegerField(blank=True, null=True)
    ref = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-id']

class Currency(models.Model):
    abbr = models.CharField(max_length=50)
    currency = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    qrcode = models.ImageField(upload_to='qrcode', blank=True, null=True)
    ref = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.abbr

class Deposite(models.Model):
    amount = models.IntegerField(blank=True, null=True)
    payment_method = models.ForeignKey('Currency', on_delete=models.CASCADE, blank=True, null=True)
    plan = models.CharField(max_length=100, blank=True, null=True)
    status = models.IntegerField(default=1, blank=True, null=True)  # 1 --> pending, 2 --> success, 3 --> expire
    image = models.ImageField(upload_to='prove', blank=True, null=True, default='noimage.jpg')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expire_time = models.DateTimeField(blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now, blank=True, null=True)
    ref = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if not self.date_created:
            self.date_created = timezone.now()
        self.expire_time = self.date_created + timedelta(seconds=3600)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-date_created']

        
class Withdrawal(models.Model):
    amount = models.IntegerField()
    payment_method = models.CharField(max_length=100, blank=True, null=True)
    status = models.IntegerField(default=1)  # 1 --> pending, 2 --> success, 3 --> expire
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mode = models.CharField(max_length=30)
    bank_name = models.CharField(max_length=30, blank=True, null=True)
    acct_name = models.CharField(max_length=30, blank=True, null=True)
    wallet_address = models.CharField(max_length=100, blank=True, null=True)
    cashapp_tag = models.CharField(max_length=100, blank=True, null=True)
    paypal_email = models.CharField(max_length=100, blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)
    ref = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.user.username

    class Meta:
        ordering = ['-date_created']
    
class CopiedTrade(models.Model):
    trade = models.ForeignKey(Trader, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pending = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    ref = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.user.username
    
class ContractPaymentMethod(models.Model):
    name = models.CharField(max_length=25)
    
    def __str__(self):
        return self.name
    
class TakeTrade(models.Model):
    crypto = models.ForeignKey(NewCoin, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trader = models.ForeignKey(Trader, on_delete=models.CASCADE)
    profit = models.IntegerField(default=0)
    time = models.IntegerField(default=0)
    mode = models.CharField(max_length=10, default='buy')
    open_trade = models.BooleanField(default=True)
    amount = models.CharField(max_length=30)
    expire_time = models.DateTimeField()
    ref = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField()
    
    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        date_before = datetime.now()
        self.expire_time = date_before + timedelta(seconds=int(self.time)*60)
        self.date_created = date_before
        super(TakeTrade, self).save(*args, **kwargs)