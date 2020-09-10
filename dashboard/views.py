from django.shortcuts import render, reverse, redirect
from .forms import buatLaporanForm
from django.views.decorators.csrf import csrf_exempt
from collections import namedtuple
from django.db import connection
import PIL
from PIL import Image
import os
from io import BytesIO
import base64
import re
import pathlib



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

    if request.method == 'POST':
        print('yey')
        # print(request.POST['imageDataURL'], False)
        imageDataURL = request.POST['imageDataURL']
        print(pathlib.Path(__file__).parent.absolute())
        current_path = pathlib.Path(__file__).parent.absolute()
        image_data = re.sub('^data:image/.+;base64,', '', imageDataURL)
        im1 = Image.open(BytesIO(base64.b64decode(image_data)))
        laporan_path = '/static/img/laporan/a/laporan1.jpg'
        im1 = im1.save(str(current_path) + laporan_path)
        
    form = buatLaporanForm()
	
    args = {
        'form': form
        }
    return render(request, "buatLaporan.html", args)