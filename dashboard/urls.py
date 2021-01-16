from django.contrib import admin
from django.urls import path
from .views import dashboard, buatLaporan, detailLaporan, gantiJabatan, choose_area, choose_rsm
from django.conf.urls.static import static


app_name = 'dashboard'

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('choose_rsm/', choose_rsm, name="choose_rsm"),
    path('choose_area/', choose_area, name="choose_area"),
    path('detailLaporan/<int:id>', detailLaporan, name='detailLaporan'),
    path('buatLaporan', buatLaporan, name="buatLaporan"),
    path('gantiJabatan', gantiJabatan, name="gantiJabatan"),
]

