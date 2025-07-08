
path('payment/request/', views.payment_request, name='payment_request'),path('payment/request/', views.payment_request, name='payment_request'),
from django.urls import path
from . import views

urlpatterns = [
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/webhook/', views.payment_webhook, name='payment_webhook'),
    path('profile/', views.profile, name='profile'),
]