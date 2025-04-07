from django.urls import path
from . import views
from .views import  make_payment, request_payment, mark_notification_read

urlpatterns = [
    path('', views.home, name='home'),

    path('make_payment/<int:user_id>/', make_payment, name='make_payment'),
    path('request_payment/<int:user_id>/', request_payment, name='request_payment'),
    path('mark-notification-read/<int:notification_id>/', mark_notification_read, name='mark_notification_read'),
    path('mark_notification_read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
]