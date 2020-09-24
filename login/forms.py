from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms



class CreateUserForm(forms.Form):
	email = forms.EmailField(required=True, max_length=100)
	password = forms.CharField(required=True, widget=forms.PasswordInput, min_length=8)
	username = forms.CharField(required=True, max_length = 20)


class Login(forms.Form):
	password = forms.CharField(required=True, widget=forms.PasswordInput)
	username = forms.CharField(required=True, max_length = 20)


	