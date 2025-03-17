from django.shortcuts import render
from django.http import JsonResponse

# Define the conversion rates (hardcoded for simplicity)
CONVERSION_RATES = {
    ('GBP', 'USD'): 1.29,
    ('USD', 'GBP'): 0.77,
    ('GBP', 'EUR'): 1.19,
    ('EUR', 'GBP'): 0.83,
    ('USD', 'EUR'): 0.91,
    ('EUR', 'USD'): 1.08,
    ('GBP', 'GBP'): 1.0,
    ('USD', 'USD'): 1.0,
    ('EUR', 'EUR'): 1.0,
}


def convert_currency_form(request, currency1, currency2, amount):
    try:
        # Convert the amount to a float
        amount = float(amount)

        # Retrieve the conversion rate
        rate = CONVERSION_RATES.get((currency1, currency2))

        # Check if the conversion rate is valid
        if rate is None:
            return render(request, 'currency_service/conversion.html',
                          {'error': 'Invalid currency pair or conversion not supported.'})

        # Calculate the converted amount
        converted_amount = round(amount * rate, 2)

        # Render the template with the results
        return render(request, 'currency_service/conversion.html', {
            'converted_amount': converted_amount,
            'currency1': currency1,
            'currency2': currency2,
            'rate': rate,
            'amount': amount
        })

    except ValueError:
        return render(request, 'currency_service/conversion.html',
                      {'error': 'Invalid amount. Please provide a numeric value.'})
