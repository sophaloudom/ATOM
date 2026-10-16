from django.conf import settings
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=180, db_index=True)
    store = models.CharField(max_length=80)
    category = models.CharField(max_length=60)
    emoji = models.CharField(max_length=10, default='🛒')
    unit = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    regular_price = models.DecimalField(max_digits=8, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(price__gte=0, regular_price__gte=0), name='positive_prices')]
    @property
    def saving(self):
        return max(self.regular_price - self.price, 0)
    @property
    def discount(self):
        return round((1-self.price/self.regular_price)*100) if self.regular_price and self.price < self.regular_price else 0
    def __str__(self): return self.name

class Watch(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','product'], name='unique_watch')]

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=240)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    emailed = models.BooleanField(default=False)
    class Meta: ordering = ['-created_at']

class Departure(models.Model):
    city = models.CharField(max_length=20, default='auckland')
    route = models.CharField(max_length=30)
    destination = models.CharField(max_length=150)
    mode = models.CharField(max_length=20, default='Bus')
    minutes = models.PositiveIntegerField()
    status = models.CharField(max_length=160, default='On time')

class ServiceAlert(models.Model):
    city = models.CharField(max_length=20, default='auckland')
    title = models.CharField(max_length=180)
    description = models.TextField()
    kind = models.CharField(max_length=20, choices=[('weather','Weather'),('transport','Transport')])
    active = models.BooleanField(default=True)

class AlertPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    city = models.CharField(max_length=20, choices=[('auckland','Auckland'),('wellington','Wellington')], default='auckland')
    weather = models.BooleanField(default=True)
    transport = models.BooleanField(default=True)
