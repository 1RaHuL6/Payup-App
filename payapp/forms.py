from django import forms

class PaymentForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=10, decimal_places=2,
        label="Enter Amount",
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

