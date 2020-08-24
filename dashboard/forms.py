from django import forms
from django.db import connection
from collections import namedtuple

class buatLaporanForm(forms.Form):
    kondisi_umum = forms.CharField(label='Kondisi Umum', max_length=100, widget=forms.Textarea(attrs={'class': 'form-control', 'style': 'box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1); border-radius: 10px;'}),)
    aktivitas_kompetitor = forms.CharField(label='Aktivitas Kompetitor', max_length=100, widget=forms.Textarea(attrs={'class': 'form-control', 'style': 'box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1); border-radius: 10px;'}),)
    laporan_kegiatan = forms.CharField(label='Laporan Kegiatan', max_length=100, widget=forms.Textarea(attrs={'class': 'form-control', 'style': 'box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1); border-radius: 10px;'}),)
    fokus_produk = forms.CharField(label='Fokus Produk', required= False, max_length=30, widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1); border-radius: 10px;'}),)
    lain_lain = forms.CharField(label='Lain-lain', max_length=100, widget=forms.Textarea(attrs={'class': 'form-control', 'style': 'box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1); border-radius: 10px;'}),)
    deskripsi_foto = forms.CharField(label='Deskripsi Foto', max_length=100, widget=forms.Textarea(attrs={'class': 'form-control', 'style': 'box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1); border-radius: 10px;'}),)