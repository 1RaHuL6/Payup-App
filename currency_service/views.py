from django.http import JsonResponse

# Hardcoded conversion rates
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

def conversion(request, currency1, currency2, amount_of_currency1):

    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)


    if (currency1, currency2) not in CONVERSION_RATES:
        return JsonResponse({'error': 'Invalid currency pair or conversion not supported'}, status=400)

    try:
        amount = float(amount_of_currency1)
    except ValueError:
        return JsonResponse({'error': 'Invalid amount. Please provide a numeric value.'}, status=400)


    rate = CONVERSION_RATES[(currency1, currency2)]
    converted_amount = round(amount * rate, 2)

    #  response
    return JsonResponse({
        'currency1': currency1,
        'currency2': currency2,
        'amount': amount,
        'conversion_rate': rate,
        'converted_amount': converted_amount
    })
