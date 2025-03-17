from django import forms

class CurrencyConversionForm(forms.Form):
    CURRENCY_CHOICES = [
        ('GBP', 'British Pound (£)'),
        ('USD', 'US Dollar ($)'),
        ('EUR', 'Euro (€)'),
    ]

    currency1 = forms.ChoiceField(choices=CURRENCY_CHOICES, label="From Currency")
    currency2 = forms.ChoiceField(choices=CURRENCY_CHOICES, label="To Currency")
    amount = forms.DecimalField(max_digits=10, decimal_places=2, label="Amount")
