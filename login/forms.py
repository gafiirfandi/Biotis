from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms



class CreateUserForm(forms.Form):
	email = forms.CharField(max_length = 50)
	password = forms.CharField(widget=forms.PasswordInput)
	username = forms.CharField(max_length = 20)


class Login(forms.Form):
	password = forms.CharField(widget=forms.PasswordInput)
	username = forms.CharField(max_length = 20)


	