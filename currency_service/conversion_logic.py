# currency_service/logic.py

# Hardcoded conversion rates
CONVERSION_RATES = {
    ('GBP', 'USD'): 1.29, ('USD', 'GBP'): 0.77,
    ('GBP', 'EUR'): 1.19, ('EUR', 'GBP'): 0.83,
    ('USD', 'EUR'): 0.91, ('EUR', 'USD'): 1.10,
    ('GBP', 'GBP'): 1.0, ('USD', 'USD'): 1.0, ('EUR', 'EUR'): 1.0,
}

def calculate_conversion(currency1, currency2, amount):
    """
    Calculates the converted amount for two currencies.
    Returns a dictionary with the results, or raises an error.
    """
    if (currency1, currency2) not in CONVERSION_RATES:
        raise ValueError('Invalid currency pair or conversion not supported')

    rate = CONVERSION_RATES[(currency1, currency2)]
    converted_amount = round(float(amount) * rate, 2)

    return {
        'currency1': currency1,
        'currency2': currency2,
        'amount': float(amount),
        'conversion_rate': rate,
        'converted_amount': converted_amount
    }