from django.urls import path
from . import views
from .views import  make_payment, request_payment, handle_payment_request, mark_notification_read

urlpatterns = [
    path('', views.home, name='home'),

    path('make_payment/<int:user_id>/', make_payment, name='make_payment'),
    path('request_payment/<int:user_id>/', request_payment, name='request_payment'),
    path('payment_request/<int:request_id>/<str:action>/', handle_payment_request, name='handle_payment_request'),
    path('mark-notification-read/<int:notification_id>/', mark_notification_read, name='mark_notification_read'),
]