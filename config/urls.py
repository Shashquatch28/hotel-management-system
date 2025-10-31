"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from booking import views as booking_views  

urlpatterns = [
    path("admin/", admin.site.urls), # URL for Admin 
    path('register/', booking_views.register, name='register'), # URL for User Registration
    path('', booking_views.home, name='home'), 
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html' 
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), # URL for Login
    path('hotels/', booking_views.hotel_list, name='hotel-list'),
    path('hotels/<int:hotel_id>/', booking_views.hotel_detail, name='hotel-detail'), # URL for Hotel View
    path('my-bookings/', booking_views.my_bookings, name='my-bookings'), # URL for Bookings
]
