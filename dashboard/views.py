from django.shortcuts import render, reverse, redirect
from .forms import buatLaporanForm
from django.views.decorators.csrf import csrf_exempt
from collections import namedtuple
from django.db import connection


def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def dashboard(request):
    if 'logged_in' not in request.session or not request.session['logged_in']:
        return redirect('login:loginPage')
    else:
        cursor = connection.cursor()
        
        return render(request, 'dashboard.html')

def buatLaporan(request):
    form = buatLaporanForm()
	
    args = {
        'form': form
        }
    return render(request, "buatLaporan.html", args)