from django.contrib import admin
from django.urls import path
from .views import dashboard, buatLaporan, detailLaporan, gantiJabatan, ganti_jabatan, rsm_area, area
from django.conf import settings
from django.conf.urls.static import static


app_name = 'dashboard'

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('detailLaporan/<int:id>', detailLaporan, name='detailLaporan'),
    path('buatLaporan', buatLaporan, name="buatLaporan"),
    path('gantiJabatan', gantiJabatan, name="gantiJabatan"),
    path('ganti_jabatan', ganti_jabatan, name="ganti_jabatan"),
    path('rsm_area', rsm_area, name="rsm_area"),
    path('area', area, name="area"),
]

