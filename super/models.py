from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify
import uuid

# Create your models here.

class Role(models.Model):
    role = models.CharField(max_length=30)
    keyword = models.SlugField()
    active = models.BooleanField(default=True)
    created_on = models.DateTimeField(default=timezone.now)
    
    def save(self, *args, **kwargs):
        self.keyword = slugify(self.role)
        super(Role, self).save(*args, **kwargs)

    def __str__(self):
        return self.role
    
class Trader(models.Model):
    name = models.CharField(max_length=100)
    win = models.IntegerField(default=0, blank=True, null=True)
    loss = models.IntegerField(default=0, blank=True, null=True)
    win_rate = models.IntegerField(default=0)
    profit = models.IntegerField(default=0)
    image = models.ImageField(upload_to='trade', default='passport.jpg', blank=True, null=True)
    followers = models.IntegerField(default=0)
    ref = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name
    
class Coin(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    type = models.CharField(max_length=10)
    
    def __str__(self):
        return self.name
    
class NewCoin(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    symbol = models.CharField(max_length=100)
    image = models.CharField(max_length=200)
    stock_image = models.ImageField(blank =True, null=True, default='stock.jpg')
    type = models.CharField(max_length=10)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['id']
        
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    mobile = models.CharField(max_length=20)
    subject = models.CharField(max_length=100)
    message = models.TextField(max_length=1000)
    
    def __str__(self):
        return self.name
    
class Currency(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    symbol = models.CharField(max_length=100)
    decimal = models.IntegerField()
    type = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class Crypto(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    symbol = models.CharField(max_length=100)
    image = models.CharField(max_length=200)
    type = models.CharField(max_length=200,default='crypto')
    
    def __str__(self):
        return self.name
    
class Forex(models.Model):
    name = models.CharField(max_length=100)
    code_n = models.CharField(max_length=100)
    code = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    symbol = models.CharField(max_length=100)
    sign = models.CharField(max_length=100)
    image = models.CharField(max_length=200)
    type = models.CharField(max_length=200,default='forex')
    
    def save(self, *args, **kwargs):
        self.code = slugify(self.name)
        super(Forex, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
class StockList(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    symbol = models.CharField(max_length=100)
    image = models.ImageField(blank =True, null=True, default='stock.jpg')
    type = models.CharField(max_length=200,default='stock')
    
    def __str__(self):
        return self.name