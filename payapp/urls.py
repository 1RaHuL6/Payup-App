from django.urls import path
from . import views
from .views import  make_payment, request_payment


urlpatterns = [
    path('', views.home, name='home'),

    path('make_payment/<int:user_id>/', make_payment, name='make_payment'),
    path('request_payment/<int:user_id>/', request_payment, name='request_payment'),

    path('accept/<int:request_id>/', views.accept_request, name='accept_request'),
    path('reject/<int:request_id>/', views.reject_request, name='reject_request'),

]