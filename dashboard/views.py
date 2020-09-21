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
from django.conf import settings




def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def dashboard(request):
    email = request.session['email']
    if 'logged_in' not in request.session or not request.session['logged_in']:
        return redirect('login:loginPage')
    else:
        cursor = connection.cursor()
        
        cursor.execute("SELECT username from pengguna where email = '"+email+"';")
        username = cursor.fetchone()[0]

        cursor.execute("SELECT role from profile where email = '"+email+"';")
        role = cursor.fetchone()[0]

        cursor.execute('SELECT path_foto from laporan;')
        foto = cursor.fetchall()

        cursor.execute('SELECT waktu from laporan;')
        waktu = cursor.fetchall()

        cursor.execute('SELECT kondisi from laporan;')
        kondisi = cursor.fetchall()
    
        cursor.execute('SELECT kompetitor from laporan;')
        kompetitor = cursor.fetchall()

        cursor.execute('SELECT laporan from laporan;')
        laporan = cursor.fetchall()

        cursor.execute('SELECT fokus_produk from laporan;')
        fokus_produk = cursor.fetchall()

        cursor.execute('SELECT other from laporan;')
        lain_lain = cursor.fetchall()

        cursor.execute('SELECT count(*) from laporan;')
        size = cursor.fetchone()[0]

        data = []

        for i in range(size):
            data.append({'foto': foto[i][0], 'waktu': waktu[i][0], 'kondisi': kondisi[i][0], 'kompetitor': kompetitor[i][0], 'laporan': laporan[i][0], 'fokus_produk': fokus_produk[i][0], 'lain_lain':lain_lain[i][0]})
        
                    
        return render(request, 'dashboard.html', {'data': data, 'username':username, 'role':role})

def buatLaporan(request):

    if request.method == 'POST':
        # print(request.POST['imageDataURL'], False)
        kondisi_umum = request.POST['kondisi_umum']
        aktivitas_kompetitor = request.POST['aktivitas_kompetitor']
        laporan_kegiatan = request.POST['laporan_kegiatan']
        fokus_produk = request.POST['fokus_produk']
        lain_lain = request.POST['lain_lain']
        deskripsi_foto = request.POST['deskripsi_foto']
        imageDataURL = request.POST['imageDataURL']
        # current_path = pathlib.Path(__file__).parent.absolute()
        current_path = settings.BASE_DIR
        # print(current_path)
        image_data = re.sub('^data:image/.+;base64,', '', imageDataURL)
        im1 = Image.open(BytesIO(base64.b64decode(image_data)))

        laporan_path = '/staticfiles/img/user' # {email}/{date}/laporan1.jpg
        # laporan_path = 'img/user'
        email = request.session['email']

        cursor = connection.cursor()
        cursor.execute("SELECT max(id_file) FROM laporan;")
        id_file = cursor.fetchone()[0]

        cursor.execute("SELECT now();")
        waktu = cursor.fetchone()[0]

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
        date_today = date.today()
        path += '/' + str(date_today)
        if not(os.path.isdir(path)):
            os.mkdir(path)
        path += '/laporan' +str(id_file) + '.jpg'
        im1 = im1.save(path)
        static_path = 'img/user' + '/' + email + '/laporan' + '/' + str(date_today) + '/laporan' +str(id_file) + '.jpg'

        cursor.execute("INSERT INTO laporan (email, kondisi, kompetitor, laporan, fokus_produk, other, foto_laporan, id_file, path_foto, waktu) VALUES('"+email+"', '"+kondisi_umum+"', '"+aktivitas_kompetitor+"', '"+laporan_kegiatan+"', '"+fokus_produk+"', '"+lain_lain+"', '"+deskripsi_foto+"', '"+str(id_file)+"', '"+static_path+"', '"+str(waktu)+"');")
        
        
        
    form = buatLaporanForm()
	
    args = {
        'form': form
        }
    return render(request, "buatLaporan.html", args)


def detailLaporan(request):
    return render(request, 'detailLaporan.html')


