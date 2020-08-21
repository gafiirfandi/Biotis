from django.contrib import admin
from django.urls import path
from .views import dasboard, buatLaporan
from django.conf import settings
from django.conf.urls.static import static


app_name = 'dasboard'

urlpatterns = [
    path('', dasboard, name='dasboard'),
    path('buatLaporan', buatLaporan, name="buatLaporan"),
]