from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
CURRENCY_CHOICES = [
    ('GBP', 'GB Pounds'),
    ('USD', 'US Dollars'),
    ('EUR', 'Euros'),
]

class UserDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='GBP')

    def __str__(self):
        return self.user.username
