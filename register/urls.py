from django.urls import path
from . import views
from .views import admin_dashboard, admin_register_view


urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home, name='home'),
    path('admin-login/', views.admin_login, name='login_admin'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-register/', admin_register_view, name='admin_register'),
]