  
from django.urls import path
from . import views

app_name = 'login'

urlpatterns = [
    path('register/', views.registerPage, name="register"),
    path('reset/', views.reset, name="reset"),
    path('verification/', views.verification, name="verification"),
    path('verified/', views.verified, name="verified"),
    path('failed_verified/', views.failed_verified, name="failed_verified"),
	path('', views.loginPage, name="loginPage"),
    path('activate/<uidb64>/<token>/',views.activate, name='activate'),  
    path('logout/', views.logoutUser, name="logout"),
]