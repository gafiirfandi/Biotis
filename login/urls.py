  
from django.urls import path
from . import views

app_name = 'login'

urlpatterns = [
    path('register/', views.registerPage, name="register"),
	path('loginPage/', views.loginPage, name="loginPage"),  
    path('logout/', views.logoutUser, name="logout")
]