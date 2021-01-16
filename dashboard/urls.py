from django.contrib import admin
from django.urls import path
<<<<<<< HEAD
from .views import dashboard, buatLaporan, detailLaporan,ganti_jabatan
=======
from .views import dashboard, buatLaporan, detailLaporan, gantiJabatan
>>>>>>> 5051ebb27472fa4fe63f11bd772eef0ffff29e70
from django.conf import settings
from django.conf.urls.static import static


app_name = 'dashboard'

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('detailLaporan/<int:id>', detailLaporan, name='detailLaporan'),
    path('buatLaporan', buatLaporan, name="buatLaporan"),
<<<<<<< HEAD
    path('ganti_jabatan', ganti_jabatan, name="ganti_jabatan"),
=======
    path('gantiJabatan', gantiJabatan, name="gantiJabatan"),
>>>>>>> 5051ebb27472fa4fe63f11bd772eef0ffff29e70
]

