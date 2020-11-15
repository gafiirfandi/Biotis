  
from django.urls import path
from . import views

app_name = 'login'

urlpatterns = [
    path('register/', views.registerPage, name="register"),
    path('reset/', views.reset, name="reset"),
	path('', views.loginPage, name="loginPage"),
    path('activate/<uidb64>/<token>/',views.activate, name='activate'),  
    path('logout/', views.logoutUser, name="logout")
]