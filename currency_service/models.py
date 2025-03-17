from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Extend Django's User model
class CustomUser(AbstractUser):
    CURRENCY_CHOICES = [
        ('GBP', 'British Pound (£)'),
        ('USD', 'US Dollar ($)'),
        ('EUR', 'Euro (€)'),
    ]
    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",  # Change related_name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_permissions_set",  # Change related_name
        blank=True
    )


    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='GBP')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)

    def save(self, *args, **kwargs):
        # Convert balance based on currency
        conversion_rates = {
            'GBP': 1.0,
            'USD': 1.25,
            'EUR': 1.15,
        }
        self.balance = 750 * conversion_rates.get(self.currency, 1.0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.username} - {self.currency} {self.balance}'
