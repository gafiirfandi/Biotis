from django.contrib import admin
from django.urls import path
from .views import login
from django.conf import settings
from django.conf.urls.static import static


app_name = 'login'

urlpatterns = [
    path('',login,name='login'),
]