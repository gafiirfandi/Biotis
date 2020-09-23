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
from datetime import datetime


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
        if request.method == "POST":            
            cursor.execute('SELECT * from laporan WHERE is_reviewed = \'false\';')
        else:
            cursor.execute('SELECT * from laporan;')

        data_query = namedtuplefetchall(cursor)
        cursor.execute('SELECT count(*) from laporan;')


        data = []
        for item in data_query:
            timestamptz = item[9]
            print(timestamptz)
            time = timestamptz.strftime("%H:%M")
            date = timestamptz.strftime("%A, %d %b %Y")
            print(time)
            print(date)
            data.append({'item': item, 'time': time, 'date': date})

        print(data)
        size = cursor.fetchone()[0]
        return render(request, 'dashboard.html', {'data': data})


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
        print(current_path)

        laporan_path = '/dashboard/static/img/user' # {email}/{date}/laporan1.jpg
        # laporan_path = 'img/user'
        email = request.session['email']

        cursor = connection.cursor()
        cursor.execute("SELECT max(id_file) FROM laporan;")
        id_file = cursor.fetchone()[0]

        cursor.execute("SELECT now() AT TIME ZONE 'Asia/Jakarta';")
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
        return redirect('dashboard:dashboard')
        
        
        
    form = buatLaporanForm()
    # print(settings.BASE_DIR)
	
    args = {
        'form': form
        }
    return render(request, "buatLaporan.html", args)


def detailLaporan(request, id):

    cursor = connection.cursor()

    if request.method == 'POST':
        review_action = request.POST.get('checkbox-1', False)
        if review_action == 'on':
            cursor.execute("UPDATE laporan SET is_reviewed = 'true' WHERE id_file='" + str(id) + "';")
        else:
            cursor.execute("UPDATE laporan SET is_reviewed = 'false' WHERE id_file='" + str(id) + "';")
        

    
    cursor.execute("SELECT * FROM laporan WHERE id_file='" + str(id) + "';")

    detail_data = namedtuplefetchall(cursor)[0]

    cursor.execute("SELECT email FROM laporan WHERE id_file='" + str(id) + "';")
    email = cursor.fetchone()[0]

    cursor.execute("SELECT username FROM pengguna WHERE email='" + email + "';")
    username = cursor.fetchone()[0]

    timestamptz = detail_data[9]
    time = timestamptz.strftime("%H:%M")
    date = timestamptz.strftime("%A, %d %B %Y")

    return render(request, 'detailLaporan.html', {'data': detail_data, 'username': username, 'date': date, 'time': time})


