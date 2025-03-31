from django.urls import path
from .views import conversion

urlpatterns = [
    path('conversion/<str:currency1>/<str:currency2>/<str:amount_of_currency1>/', conversion, name='currency_conversion'),
]
