from django.contrib import admin
from django.urls import path
from .views import dashboard, buatLaporan, detailLaporan
from django.conf import settings
from django.conf.urls.static import static


app_name = 'dashboard'

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('detailLaporan', detailLaporan, name='detailLaporan'),
    path('buatLaporan', buatLaporan, name="buatLaporan"),
]