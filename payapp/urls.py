from django.urls import path
from . import views
from .views import  make_payment

urlpatterns = [
    path('', views.home, name='home'),

    path('make_payment/<int:user_id>/', make_payment, name='make_payment'),
]