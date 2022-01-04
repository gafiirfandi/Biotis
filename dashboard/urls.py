from django.contrib import admin
from django.urls import path
from .views import dashboard, buatLaporan, detailLaporan, error_403, error_404, ganti_jabatan, rsm_area, sumatera, jawa, timur, laporan_rsm, laporan_daerah, laporan_daerah_am, pilih_user
from django.conf import settings
from django.conf.urls.static import static


app_name = 'dashboard'

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('detailLaporan/<int:id>', detailLaporan, name='detailLaporan'),
    path('buatLaporan', buatLaporan, name="buatLaporan"),
    path('pilih_user', pilih_user, name="pilih_user"),
    path('ganti_jabatan/<str:email>', ganti_jabatan, name="ganti_jabatan"),
    path('rsm_area', rsm_area, name="rsm_area"),
    path('sumatera', sumatera, name="sumatera"),
    path('jawa', jawa, name="jawa"),
    path('indonesiaTimur', timur, name="timur"),
    path('laporan_rsm/<str:pulau>', laporan_rsm, name="laporan_rsm"),
    path('laporan_daerah/<str:pulau>', laporan_daerah, name="laporan_daerah"),
    path('laporan_daerah_am/<str:pulau>', laporan_daerah_am, name="laporan_daerah_am"),
    path('error', error_404, name="error_404"),
    path('error403', error_403, name="error_403")
]

