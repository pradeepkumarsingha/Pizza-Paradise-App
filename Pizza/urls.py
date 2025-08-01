"""
URL configuration for Pizza project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Home.views import home, menu, cart, checkout, login_view, register, logout_view, profile, add_to_cart, remove_from_cart, payment_success
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from django.contrib.auth import views as auth_views
from Home.views import *

urlpatterns = [
    path('', home, name='home'),
    path('menu/', menu, name='menu'),
    path('cart/', cart, name='cart'),
    path('checkout/', checkout, name='checkout'),
    path('payment/success/', payment_success, name='payment_success'),
    path('login/', login_view, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile, name='profile'),
    re_path(r'^add-to-cart/(?P<pizza_id>[0-9a-f-]+)/$', add_to_cart, name='add_to_cart'),
    re_path(r'^remove-from-cart/(?P<pizza_id>[0-9a-f-]+)/$', remove_from_cart, name='remove_from_cart'),
    
    # Password reset URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
