from django.urls import path
from . import views

app_name = 'profile'

urlpatterns = [
    path('edit/', views.editprofile, name='edit'),
    path('',views.profile, name='profile')
    
]