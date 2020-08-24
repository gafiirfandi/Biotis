from django.shortcuts import render

def index(request):
    nama = "lado"
    return render(request, 'profile.html', {'nama':nama})
