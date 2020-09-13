from django.shortcuts import render, reverse, redirect
from .forms import buatLaporanForm
from django.views.decorators.csrf import csrf_exempt
from collections import namedtuple
from django.db import connection
from datetime import date
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
        kondisi_umum = request.POST['kondisi_umum']
        aktivitas_kompetitor = request.POST['aktivitas_kompetitor']
        laporan_kegiatan = request.POST['laporan_kegiatan']
        fokus_produk = request.POST['fokus_produk']
        lain_lain = request.POST['lain_lain']
        deskripsi_foto = request.POST['deskripsi_foto']
        imageDataURL = request.POST['imageDataURL']
<<<<<<< HEAD
        print(imageDataURL)
=======

>>>>>>> 923357d3f56551c23955bcc507b8f929d5729751
        print(pathlib.Path(__file__).parent.absolute())
        current_path = pathlib.Path(__file__).parent.absolute()
        image_data = re.sub('^data:image/.+;base64,', '', imageDataURL)
        im1 = Image.open(BytesIO(base64.b64decode(image_data)))

        laporan_path = '/static/img/user' # {email}/{date}/laporan1.jpg
        email = request.session['email']

        cursor = connection.cursor()
        cursor.execute("SELECT max(id_file) FROM laporan;")
        id_file = cursor.fetchone()[0]
        # print('id_file' + str(id_file))
        if id_file is None:
            id_file = 1
        else:
            id_file += 1

        path = str(current_path) + laporan_path + '/' + email
        if not(os.path.isdir(path)):
            os.mkdir(path)
        path += '/laporan'
        if not(os.path.isdir(path)):
            os.mkdir(path)
        path += '/' + str(date.today())
        if not(os.path.isdir(path)):
            os.mkdir(path)
        path += '/laporan' +str(id_file) + '.jpg'
        print(path)
        im1 = im1.save(path)

        cursor.execute("INSERT INTO laporan (email, kondisi, kompetitor, laporan, fokus_produk, other, foto_laporan, id_file, path_foto) VALUES('"+email+"', '"+kondisi_umum+"', '"+aktivitas_kompetitor+"', '"+laporan_kegiatan+"', '"+fokus_produk+"', '"+lain_lain+"', '"+deskripsi_foto+"', '"+str(id_file)+"', '"+path+"');")
        
        
        
    form = buatLaporanForm()
	
    args = {
        'form': form
        }
    return render(request, "buatLaporan.html", args)


def detailLaporan(request):
    return render(request, 'detailLaporan.html')


