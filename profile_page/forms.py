from django import forms

class FormProfile(forms.Form):

    nama_lengkap = forms.CharField(max_length=50, required=False)
    no_hp = forms.CharField(max_length=15, required=False)
    alamat = forms.CharField(max_length=100, required=False)
    jabatan = forms.CharField(max_length= 50, required=False)
    nama_atasan  = forms.CharField(max_length = 50, required=False)
    