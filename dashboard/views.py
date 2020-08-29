from django.shortcuts import render, reverse, redirect
from .forms import buatLaporanForm

# Create your views here.
def dashboard(request):
    return render(request, 'dashboard.html')

def buatLaporan(request):
    form = buatLaporanForm()
			
    args = {
        'form': form
        }
    return render(request, "buatLaporan.html", args)


def detailLaporan(request):
    return render(request, 'detailLaporan.html')