from django.http import JsonResponse
from .conversion_logic import calculate_conversion

def conversion(request, currency1, currency2, amount_of_currency1):
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET requests are allowed'}, status=405)

    try:
        result = calculate_conversion(currency1, currency2, amount_of_currency1)
        return JsonResponse(result)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception:
        return JsonResponse({'error': 'Invalid amount. Please provide a numeric value.'}, status=400)