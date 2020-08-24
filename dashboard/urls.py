from django.contrib import admin
from django.urls import path
from .views import dashboard, buatLaporan
from django.conf import settings
from django.conf.urls.static import static


app_name = 'dashboard'

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('buatLaporan', buatLaporan, name="buatLaporan"),
]