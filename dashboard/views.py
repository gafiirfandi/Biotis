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
import calendar
import random, string
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.paginator import Paginator


def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

@csrf_exempt
def dashboard(request):
    print(settings.DATA_UPLOAD_MAX_MEMORY_SIZE)
    my_date = date.today()
    hari = calendar.day_name[my_date.weekday()]
    d1 = my_date.strftime("%B %d, %Y")
    
    if 'logged_in' not in request.session or not request.session['logged_in']:    
        return redirect('login:loginPage')
    else:
        
        
        cursor = connection.cursor()
        email = request.session['email']
        
        cursor.execute("SELECT rsm FROM PROFILE WHERE email = '"+email+"';")
        rsm = cursor.fetchone()
        cursor.execute("SELECT area FROM PROFILE WHERE email = '"+email+"';")
        area = cursor.fetchone()
        if rsm[0] and not area[0]:
            return redirect('login:choose_area')
        elif not rsm[0] and area[0]:
            return redirect('login:choose_rsm')
        elif not rsm[0] and not area[0]:
            return redirect('login:choose_rsm')
        
        searching = False
        menunggu_review = False
        sudah_review = False
        tanggal_terlama = False
        tanggal_tertentu = False
        search_key = False
        
        # for key, value in request.session.items():
        #     print('{} => {}'.format(key, value))
        if request.session['role'] == 'admin':
        
            action_toggle_tanggal = ""
            if request.method == "POST" and request.POST['action'] == "searching":
                print("masuk searching")
                search = request.POST['search']
                search_key = search
                cursor.execute("select * from laporan where email SIMILAR TO '%"+search+"%' OR kondisi SIMILAR TO '%"+search+"%' OR kompetitor SIMILAR TO '%"+search+"%' OR laporan SIMILAR TO '%"+search+"%' OR fokus_produk SIMILAR TO '%"+search+"%' OR other SIMILAR TO '%"+search+"%';")
                
                searching = True
            elif request.method == "POST" and request.POST['action'] == "see-all":
                print("masuk see-all")          
                cursor.execute('SELECT * from laporan;')
                
            elif request.method == "POST" and request.POST['action'] == "menunggu-review":
                cursor.execute('SELECT * from laporan WHERE COALESCE(is_reviewed, FALSE) = FALSE;')
                searching = True
                menunggu_review = True
            elif request.method == "POST" and request.POST['action'] == "sudah-review":            
                cursor.execute("SELECT * from laporan WHERE COALESCE(is_reviewed, FALSE) = TRUE;") 
                searching = True
                sudah_review = True
            elif request.GET.get('page') is not None:
                print(request.GET.get('page'))
                print(request.GET.get('page').split())
                print(request.GET.get('page').split()[1][16:])
                print(request.GET.get('page').split()[2][13:])
                if request.GET.get('page').split()[1][16:] == "True":
                    print("Horay")
                    cursor.execute('SELECT * from laporan WHERE COALESCE(is_reviewed, FALSE) = FALSE;')
                    menunggu_review = True
                    searching = True
                elif request.GET.get('page').split()[2][13:] == "True":
                    print("Hore!")
                    cursor.execute('SELECT * from laporan WHERE COALESCE(is_reviewed, FALSE) = TRUE;')
                    sudah_review = True
                    searching = True
                elif request.GET.get('page').split()[3][16:] == "True":
                    cursor.execute("SELECT * from laporan ORDER BY waktu ASC;")
                    action_toggle_tanggal = "tanggal-terbaru"
                    tanggal_terlama = True
                    searching = True
                elif request.GET.get('page').split()[4][17:] != "False":
                    tanggal_tertentu = request.GET.get('page').split()[4][17:]
                    searching = True
                    cursor.execute("SELECT * from laporan WHERE waktu::date = '" + tanggal_tertentu + "' ORDER BY waktu ASC;")
                elif request.GET.get('page').split()[5][11:] != "False":
                    search_key = request.GET.get('page').split()[5][11:]
                    cursor.execute("select * from laporan where email SIMILAR TO '%"+search_key+"%' OR kondisi SIMILAR TO '%"+search_key+"%' OR kompetitor SIMILAR TO '%"+search_key+"%' OR laporan SIMILAR TO '%"+search_key+"%' OR fokus_produk SIMILAR TO '%"+search_key+"%' OR other SIMILAR TO '%"+search_key+"%';") 
                    searching = True
                    
                    
                    
                    
                else:
                    cursor.execute('SELECT * from laporan ORDER BY waktu DESC;')
                    
            elif request.method == "POST" and request.POST['action'] == "tanggal-terbaru":
                cursor.execute("SELECT * from laporan ORDER BY waktu DESC;")
                action_toggle_tanggal = "tanggal-terlama"
            elif request.method == "POST" and request.POST['action'] == "tanggal-terlama":
                cursor.execute("SELECT * from laporan ORDER BY waktu ASC;")
                action_toggle_tanggal = "tanggal-terbaru"
                tanggal_terlama = True

            elif request.method == "POST" and request.POST['action'] == "datepicker":
                # print("yay")
                # print("POST:", request.POST['date'])
                tanggal = request.POST['date']
                tanggal_tertentu = tanggal[-4:] + "-" + tanggal[3:5] + "-" + tanggal[0:2]
                if tanggal == "":
                    return redirect('dashboard:dashboard')
                else:
                    cursor.execute("SELECT * from laporan WHERE waktu::date = '" + tanggal_tertentu + "' ORDER BY waktu ASC;")
                
            else:
                # print("masuk else")
                cursor.execute('SELECT * from laporan ORDER BY waktu DESC;')

            data_query = namedtuplefetchall(cursor)
            cursor.execute('SELECT count(*) from laporan;')

            cursor.execute("SELECT count(*) from laporan WHERE COALESCE(is_reviewed, FALSE) = TRUE;")
            count_is_reviewed = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) from laporan WHERE COALESCE(is_reviewed, FALSE) = FALSE;")
            count_is_not_reviewed = cursor.fetchone()[0]

            cursor.execute("SELECT username FROM pengguna WHERE email = '" + email + "';")
            username = cursor.fetchone()[0]

            cursor.execute("SELECT role FROM profile WHERE email = '" + email + "';")
            role = cursor.fetchone()[0]
            data = []
            for item in data_query:
                timestamptz = item[9]
                # print(timestamptz)
                time = timestamptz.strftime("%H:%M")
                timestamp_tanggal = timestamptz.strftime("%A, %d %b %Y")
                # print(time)
                # print(date)
                data.append({'item': item, 'time': time, 'date': timestamp_tanggal})
                
            # paginator = Paginator(data, 5)
            # page_number = request.GET.get('page')
            # page_obj = paginator.get_page(page_number)
            
            # p = Paginator(data, 10)
            # page_number = request.GET.get('page')
            # page_obj = p.get_page(page_number)
            
            p = Paginator(data, 10)
            if request.GET.get('page') is not None:
                page_number = request.GET.get('page').split()[0]
            else:
                page_number = request.GET.get('page')
            page_obj = p.get_page(page_number)
            print(p.num_pages, " - pages!!!!")

            # print(data)
            return render(request, 'dashboard.html', {'data': page_obj,'hari':hari,'tanggal':d1,'toggle_action': action_toggle_tanggal, 'reviewed':count_is_reviewed, 'not_reviewed':count_is_not_reviewed, 'username':username, 'role':role, 'back':searching, "menunggu_review": menunggu_review, "sudah_review": sudah_review, "tanggal_terlama": tanggal_terlama, "tanggal_tertentu": tanggal_tertentu, "search_key": search_key})

        elif request.session['role'] == 'karyawan' or request.session['role'] == 'rsm' or request.session['role'] == 'am':
            action_toggle_tanggal = ""
            if request.method == "POST" and request.POST['action'] == "searching":
                search = request.POST['search']
                search_key = search
                cursor.execute("select * from laporan where email = '"+request.session['email']+"' AND (kondisi SIMILAR TO '%"+search+"%' OR kompetitor SIMILAR TO '%"+search+"%' OR laporan SIMILAR TO '%"+search+"%' OR fokus_produk SIMILAR TO '%"+search+"%' OR other SIMILAR TO '%"+search+"%');") 
                if search == '':
                    cursor.execute("SELECT * from laporan WHERE email = '" + request.session['email'] + "';")
                searching = True
            elif request.method == "POST" and request.POST['action'] == "see-all":            
                cursor.execute("SELECT * from laporan WHERE email = '" + request.session['email'] + "';")

            elif request.method == "POST" and request.POST['action'] == "menunggu-review":            
                cursor.execute("SELECT * from laporan WHERE COALESCE(is_reviewed, FALSE) = FALSE AND email = '" + request.session['email'] + "';")
                searching = True
                menunggu_review = True

            elif request.method == "POST" and request.POST['action'] == "sudah-review":            
                cursor.execute("SELECT * from laporan WHERE COALESCE(is_reviewed, FALSE) = TRUE AND email = '" + request.session['email'] + "';")
                searching = True
                sudah_review = True
                
            elif request.GET.get('page') is not None:
                print(request.GET.get('page'))
                print(request.GET.get('page').split())
                print(request.GET.get('page').split()[1][16:])
                print(request.GET.get('page').split()[2][13:])
                if request.GET.get('page').split()[1][16:] == "True":
                    print("Horay")
                    cursor.execute("SELECT * from laporan WHERE COALESCE(is_reviewed, FALSE) = FALSE AND email = '" + request.session['email'] + "';")
                    menunggu_review = True
                    searching = True
                elif request.GET.get('page').split()[2][13:] == "True":
                    print("Hore!")
                    cursor.execute("SELECT * from laporan WHERE COALESCE(is_reviewed, FALSE) = TRUE AND email = '" + request.session['email'] + "';")
                    sudah_review = True
                    searching = True
                elif request.GET.get('page').split()[3][16:] == "True":
                    cursor.execute("SELECT * from laporan WHERE email = '" + request.session['email'] + "' ORDER BY waktu ASC;")
                    action_toggle_tanggal = "tanggal-terbaru"
                    tanggal_terlama = True
                    searching = True
                elif request.GET.get('page').split()[4][17:] != "False":
                    tanggal_tertentu = request.GET.get('page').split()[4][17:]
                    searching = True
                    cursor.execute("SELECT * from laporan WHERE waktu::date = '" + tanggal_tertentu + "' AND email = '" + request.session['email'] + "' ORDER BY waktu ASC;")
                elif request.GET.get('page').split()[5][11:] != "False":
                    search_key = request.GET.get('page').split()[5][11:]
                    cursor.execute("select * from laporan where email = '"+request.session['email']+"' AND (kondisi SIMILAR TO '%"+search_key+"%' OR kompetitor SIMILAR TO '%"+search_key+"%' OR laporan SIMILAR TO '%"+search_key+"%' OR fokus_produk SIMILAR TO '%"+search_key+"%' OR other SIMILAR TO '%"+search_key+"%');") 
                    searching = True
                else:
                    cursor.execute("SELECT * from laporan WHERE email = '" + request.session['email'] + "';")

            elif request.method == "POST" and request.POST['action'] == "tanggal-terbaru":
                cursor.execute("SELECT * from laporan WHERE email = '" + request.session['email'] + "' ORDER BY waktu DESC;")
                action_toggle_tanggal = "tanggal-terlama"
                searching = True

            elif request.method == "POST" and request.POST['action'] == "tanggal-terlama":
                cursor.execute("SELECT * from laporan WHERE email = '" + request.session['email'] + "' ORDER BY waktu ASC;")
                action_toggle_tanggal = "tanggal-terbaru"
                tanggal_terlama = True
                searching = True

            elif request.method == "POST" and request.POST['action'] == "datepicker":
                tanggal = request.POST['date']
                tanggal_tertentu = tanggal[-4:] + "-" + tanggal[3:5] + "-" + tanggal[0:2]
                if tanggal == "":
                    return redirect('dashboard:dashboard')
                else:
                    cursor.execute("SELECT * from laporan WHERE email = '" + email + "' AND waktu::date = '" + tanggal_tertentu + "' ORDER BY waktu ASC;")
                    searching = True
                
            else:
                cursor.execute("SELECT * from laporan WHERE email = '" + email + "';")

            data_query = namedtuplefetchall(cursor)
            
            data = []
            for item in data_query:
                timestamptz = item[9]
                # print(timestamptz)
                time = timestamptz.strftime("%H:%M")
                timestamp_tanggal = timestamptz.strftime("%A, %d %b %Y")
                # print(time)
                # print(date)
                data.append({'item': item, 'time': time, 'date': timestamp_tanggal})

            cursor.execute("SELECT count(*) from laporan WHERE email = '" + request.session['email'] + "' AND COALESCE(is_reviewed, FALSE) = FALSE;;")
            count_is_not_reviewed = cursor.fetchone()[0]
            cursor.execute("SELECT count(*) from laporan WHERE email = '" + request.session['email'] + "' AND COALESCE(is_reviewed, FALSE) = TRUE;")
            count_is_reviewed = cursor.fetchone()[0]

            print(action_toggle_tanggal, "!!!!!!!")
            email = request.session['email']
            cursor.execute("SELECT username FROM pengguna WHERE email = '" + email + "';")
            username = cursor.fetchone()[0]

            cursor.execute("SELECT role FROM profile WHERE email = '" + email + "';")
            role = cursor.fetchone()[0]

            # paginator = Paginator(data, 10)
            # page_number = request.GET.get('page')
            # page_obj = paginator.get_page(page_number)
            
            p = Paginator(data, 10)
            if request.GET.get('page') is not None:
                page_number = request.GET.get('page').split()[0]
            else:
                page_number = request.GET.get('page')
            page_obj = p.get_page(page_number)
            print(p.num_pages, " - pages!!!!")
            
            return render(request, 'dashboardkaryawan.html', {'data': page_obj, 'toggle_action': action_toggle_tanggal,'hari':hari,'tanggal':d1, 'username': username, 'role':role, "count_is_reviewed": count_is_reviewed, 'count_is_not_reviewed': count_is_not_reviewed, 'back':searching, "menunggu_review": menunggu_review, "sudah_review": sudah_review, "tanggal_terlama": tanggal_terlama, "tanggal_tertentu": tanggal_tertentu, "search_key": search_key})

@csrf_exempt
def buatLaporan(request):
    if 'logged_in' not in request.session or not request.session['logged_in']:    
        return redirect('login:loginPage')
    else:
        if request.method == 'POST':
            # print(request.POST['imageDataURL'], False)
            kondisi_umum = request.POST['kondisi_umum']
            aktivitas_kompetitor = request.POST['aktivitas_kompetitor']
            laporan_kegiatan = request.POST['laporan_kegiatan']
            fokus_produk = request.POST['fokus_produk']
            lain_lain = request.POST['lain_lain']
            deskripsi_foto = request.POST['deskripsi_foto']
            imageDataURL = request.POST.get('imageDataURL1', None)
            imageDataURL2 = request.POST.get('imageDataURL2', None)
            imageDataURL3 = request.POST.get('imageDataURL3', None)
            imageDataURL4 = request.POST.get('imageDataURL4', None)
            imageDataURL5 = request.POST.get('imageDataURL5', None)
            file1 = request.FILES.get('file1', None)
            file2 = request.FILES.get('file2', None)
            file3 = request.FILES.get('file3', None)
    
            # current_path = pathlib.Path(__file__).parent.absolute()
            current_path = settings.BASE_DIR
            # print(current_path)
            image_list = []
            if imageDataURL:
                image_decode = re.sub('^data:image/.+;base64,', '', imageDataURL)
                im1 = Image.open(BytesIO(base64.b64decode(image_decode)))
                image_list.append(im1)
    
            if imageDataURL2:
                image_decode = re.sub('^data:image/.+;base64,', '', imageDataURL2)
                im2 = Image.open(BytesIO(base64.b64decode(image_decode)))
                image_list.append(im2)
            if imageDataURL3:
                image_decode = re.sub('^data:image/.+;base64,', '', imageDataURL3)
                im3 = Image.open(BytesIO(base64.b64decode(image_decode)))
                image_list.append(im3)
            if imageDataURL4:
                image_decode = re.sub('^data:image/.+;base64,', '', imageDataURL4)
                im4 = Image.open(BytesIO(base64.b64decode(image_decode)))
                image_list.append(im4)
            if imageDataURL5:
                image_decode = re.sub('^data:image/.+;base64,', '', imageDataURL5)
                im5 = Image.open(BytesIO(base64.b64decode(image_decode)))
                image_list.append(im5)
    
            laporan_path = '/static/img/user' # {email}/{date}/laporan1.jpg
            email = request.session['email']
    
            cursor = connection.cursor()
            cursor.execute("SELECT now() AT TIME ZONE 'Asia/Jakarta';")
            waktu = cursor.fetchone()[0]
            temp_static_path = []
            for i in range(len(image_list)):
    
                cursor.execute("SELECT max(id_file) FROM laporan;")
                id_file = cursor.fetchone()[0]
    
                if id_file is None:
                    id_file = 1 + i
                else:
                    id_file = id_file + 1 + i
    
                path = '/home/biotisst/public_html' + laporan_path + '/' + email
                if not(os.path.isdir(path)):
                    os.mkdir(path)
                path += '/laporan'
                if not(os.path.isdir(path)):
                    os.mkdir(path)
                date_today = date.today()
                path += '/' + str(date_today)
                if not(os.path.isdir(path)):
                    os.mkdir(path)
                random_img_code = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
                path += '/laporan' + str(id_file) + str(random_img_code) + '.jpg'
                image_list[i].save(path)
                # im1 = im1.save(path)
                static_path = 'img/user' + '/' + email + '/laporan' + '/' + str(date_today) + '/laporan' + str(id_file) + str(random_img_code) + '.jpg'
                temp_static_path.append(static_path)
    
            cursor.execute("SELECT max(id_file) FROM laporan;")
            insert_id_file = cursor.fetchone()[0]
            # print(id_file, "id file")
            if insert_id_file == None:
                insert_id_file = 1
            else:
                insert_id_file = insert_id_file + 1
                
            num_of_file = 0
            path1 = "NULL"
            path2 = "NULL"
            path3 = "NULL"
            if file1:
                num_of_file = 1
                path1 = '/files/' + file1.name
                # path = default_storage.save('/files/' + file1.name, ContentFile(file1.read()))
                with open('/home/biotisst/public_html/files/' + file1.name, 'wb+') as f:
                    for chunk in file1.chunks():
                        f.write(chunk)
                
                # tmp_file = os.path.join('/home/biotisst/public_html', path)
            if file2:
                num_of_file = 2
                path2 = '/files/' + file2.name
                with open('/home/biotisst/public_html/files/' + file2.name, 'wb+') as f:
                    for chunk in file2.chunks():
                        f.write(chunk)
                # path = default_storage.save('/files/' + file2.name, ContentFile(file2.read()))
                # tmp_file = os.path.join('/home/biotisst/public_html', path)
            if file3:
                num_of_file = 3
                path3 = '/files/' + file3.name
                with open('/home/biotisst/public_html/files/' + file3.name, 'wb+') as f:
                    for chunk in file3.chunks():
                        f.write(chunk)
                # path = default_storage.save('/files/' + file3.name, ContentFile(file3.read()))
                # tmp_file = os.path.join('/home/biotisst/public_html', path)
    
            if len(image_list) == 1:
                # cursor.execute("INSERT INTO laporan (email, kondisi, kompetitor, laporan, fokus_produk, other, foto_laporan, id_file, path_foto, waktu) VALUES('"+email+"', '"+kondisi_umum+"', '"+aktivitas_kompetitor+"', '"+laporan_kegiatan+"', '"+fokus_produk+"', '"+lain_lain+"', '"+deskripsi_foto+"', '"+str(insert_id_file)+"', '"+temp_static_path[0]+"', '"+str(waktu)+"');")    
                cursor.execute("INSERT INTO laporan (email, kondisi, kompetitor, laporan, fokus_produk, other, foto_laporan, id_file, path_foto, waktu, file1, file2, file3) VALUES('"+email+"', '"+kondisi_umum+"', '"+aktivitas_kompetitor+"', '"+laporan_kegiatan+"', '"+fokus_produk+"', '"+lain_lain+"', '"+deskripsi_foto+"', '"+str(id_file)+"', '"+temp_static_path[0]+"', '"+str(waktu)+"', '" + path1 + "', '" + path2 + "', '" + path3 + "');")
            elif len(image_list) == 2:
                # cursor.execute("INSERT INTO laporan (email, kondisi, kompetitor, laporan, fokus_produk, other, foto_laporan, id_file, path_foto, path_foto2, waktu) VALUES('"+email+"', '"+kondisi_umum+"', '"+aktivitas_kompetitor+"', '"+laporan_kegiatan+"', '"+fokus_produk+"', '"+lain_lain+"', '"+deskripsi_foto+"', '"+str(insert_id_file)+"', '"+temp_static_path[0]+"', '"+ temp_static_path[1] + "', '" +str(waktu)+"');")
                cursor.execute("INSERT INTO laporan (email, kondisi, kompetitor, laporan, fokus_produk, other, foto_laporan, id_file, path_foto, path_foto2, waktu, file1, file2, file3) VALUES('"+email+"', '"+kondisi_umum+"', '"+aktivitas_kompetitor+"', '"+laporan_kegiatan+"', '"+fokus_produk+"', '"+lain_lain+"', '"+deskripsi_foto+"', '"+str(id_file)+"', '"+temp_static_path[0]+"', '"+ temp_static_path[1] + "', '" +str(waktu)+"', '" + path1 + "', '" + path2 + "', '" + path3 + "');")
            elif len(image_list) == 3:
                cursor.execute("INSERT INTO laporan (email, kondisi, kompetitor, laporan, fokus_produk, other, foto_laporan, id_file, path_foto, path_foto2, path_foto3, waktu, file1, file2, file3) VALUES('"+email+"', '"+kondisi_umum+"', '"+aktivitas_kompetitor+"', '"+laporan_kegiatan+"', '"+fokus_produk+"', '"+lain_lain+"', '"+deskripsi_foto+"', '"+str(id_file)+"', '"+temp_static_path[0]+"', '"+ temp_static_path[1] + "', '" + temp_static_path[2] + "', '" +str(waktu)+"', '" + path1 + "', '" + path2 + "', '" + path3 + "');")
            elif len(image_list) == 4:
                cursor.execute("INSERT INTO laporan (email, kondisi, kompetitor, laporan, fokus_produk, other, foto_laporan, id_file, path_foto, path_foto2, path_foto3, path_foto4, waktu, file1, file2, file3) VALUES('"+email+"', '"+kondisi_umum+"', '"+aktivitas_kompetitor+"', '"+laporan_kegiatan+"', '"+fokus_produk+"', '"+lain_lain+"', '"+deskripsi_foto+"', '"+str(id_file)+"', '"+temp_static_path[0]+"', '"+ temp_static_path[1] + "', '" + temp_static_path[2] + "', '" + temp_static_path[3] + "', '" +str(waktu)+"', '" + path1 + "', '" + path2 + "', '" + path3 + "');")
            elif len(image_list) == 5:
                cursor.execute("INSERT INTO laporan (email, kondisi, kompetitor, laporan, fokus_produk, other, foto_laporan, id_file, path_foto, path_foto2, path_foto3, path_foto4, path_foto5, waktu, file1, file2, file3) VALUES('"+email+"', '"+kondisi_umum+"', '"+aktivitas_kompetitor+"', '"+laporan_kegiatan+"', '"+fokus_produk+"', '"+lain_lain+"', '"+deskripsi_foto+"', '"+str(id_file)+"', '"+temp_static_path[0]+"', '"+ temp_static_path[1] + "', '" + temp_static_path[2] + "', '" + temp_static_path[3] + "', '" + temp_static_path[4] + "', '" +str(waktu)+"', '" + path1 + "', '" + path2 + "', '" + path3 + "');")
            
            return redirect('dashboard:dashboard')
            
            
        form = buatLaporanForm()
        # print(settings.BASE_DIR)
    	
        args = {
            'form': form
            }
        return render(request, "buatLaporan.html", args)

@csrf_exempt
def detailLaporan(request, id):

    cursor = connection.cursor()

    if request.method == 'POST' and request.POST['action'] == "hapus":
        cursor.execute("SELECT path_foto, path_foto2, path_foto3, path_foto4, path_foto5 FROM laporan WHERE id_file=" + str(id) + ";")
        data_delete = namedtuplefetchall(cursor)[0]
        os.remove('/home/biotisst/public_html/static/'+data_delete[0])
        if data_delete[1] != None:
            os.remove('/home/biotisst/public_html/static/'+data_delete[1])
        if data_delete[2] != None:
            os.remove('/home/biotisst/public_html/static/'+data_delete[2])
        if data_delete[3] != None:
            os.remove('/home/biotisst/public_html/static/'+data_delete[3])
        if data_delete[4] != None:
            os.remove('/home/biotisst/public_html/static/'+data_delete[4])
        cursor.execute("DELETE FROM laporan WHERE id_file=" + str(id) + ";")
        return redirect('dashboard:dashboard')

    elif request.method == 'POST' and request.POST['action'] == "review":
        review_action = request.POST.get('checkbox-1', False)
        if review_action == 'on':
            cursor.execute("UPDATE laporan SET is_reviewed = 'true' WHERE id_file='" + str(id) + "';")
        else:
            cursor.execute("UPDATE laporan SET is_reviewed = 'false' WHERE id_file='" + str(id) + "';")
        

    
    cursor.execute("SELECT * FROM laporan WHERE id_file='" + str(id) + "';")

    detail_data = namedtuplefetchall(cursor)[0]

    cursor.execute("SELECT email FROM laporan WHERE id_file='" + str(id) + "';")
    email_laporan = cursor.fetchone()[0]


    cursor.execute("SELECT username FROM pengguna WHERE email='" + email_laporan + "';")
    username_laporan = cursor.fetchone()[0]
    
    email = request.session['email']
    cursor.execute("SELECT username FROM pengguna WHERE email = '" + email + "';")
    username = cursor.fetchone()[0]

    

    timestamptz = detail_data[9]
    time = timestamptz.strftime("%H:%M")
    date = timestamptz.strftime("%A, %d %B %Y")
    role = request.session['role']

    return render(request, 'detailLaporan.html', {'data': detail_data, 'username': username, 'username_laporan': username_laporan, 'date': date, 'time': time, 'role': role})


def searching(request):
    
    cursor = connection.cursor()
    template_a = 'dashboard.html'
    template_k = 'dashboardkaryawan.html'

    search = request.GET.get('search')
    cursor.execute("select * from laporan where email SIMILAR TO '%"+search+"%' OR kondisi SIMILAR TO '%"+search+"%' OR kompetitor SIMILAR TO '%"+search+"%' OR laporan SIMILAR TO '%"+search+"%' OR fokus_produk SIMILAR TO '%"+search+"%' OR other SIMILAR TO '%"+search+"%';")
    data_query = namedtuplefetchall(cursor)
    data = []
    for item in data_query:
        timestamptz = item[9]
        # print(timestamptz)
        time = timestamptz.strftime("%H:%M")
        date = timestamptz.strftime("%A, %d %b %Y")
        # print(time)
        # print(date)
        data.append({'item': item, 'time': time, 'date': date})

    email = request.session['email']
    cursor.execute("SELECT username FROM pengguna WHERE email = '" + email + "';")
    username = cursor.fetchone()[0]
    searching = True
    cursor.execute("SELECT role FROM profile WHERE email = '" + email + "';")
    role = cursor.fetchone()[0]
    if request.session['role'] == 'admin':
        return render(request, template_a, {'data':data, 'username':username, 'role':role, 'back':searching})
    elif request.session['role'] == 'karyawan':
        return render(request, template_k, {'data':data, 'username':username, 'role':role, 'back':searching})

@csrf_exempt        
def rsm_area(request):
	if 'logged_in' in request.session or not request.session['logged_in']:
		cursor = connection.cursor()
		email = request.session['email']
		username = request.session['username']
		cursor.execute("SELECT role from PROFILE WHERE email = '"+email+"';")
		role = cursor.fetchone()[0]
		cursor.close()
		return render(request, 'rsm_area.html',{'username':username, 'role':role})

# 		if request.method == 'POST' and request.POST['action'] == 'sumatera':
# 			return redirect('dashboard:sumatera')
# 		elif request.method == 'POST' and request.POST['action'] == 'jawa':
# 			return redirect('dashboard:jawa')
# 		elif request.method == 'POST' and request.POST['action'] == 'indonesiaTimur':
# 			return redirect('dashboard:timur')	
# 		else:
# 			return render(request,'rsm_area.html')

	else:
		return redirect('login:loginPage')

@csrf_exempt		
def sumatera(request):
	if 'logged_in' in request.session or not request.session['logged_in']:
		cursor = connection.cursor()
		email = request.session['email']
		
		username = request.session['username']
		
		cursor.execute("SELECT role from PROFILE WHERE email = '"+email+"';")
		role = cursor.fetchone()[0]
		cursor.close()

		if request.method == 'POST':
		    if role == 'admin':
		        if request.POST['action'] == 'lampung_bengkulu':
		            return redirect('dashboard:laporan_daerah', pulau="lampung bengkulu")
		        elif request.POST['action'] == 'sumatera_selatan':
		            return redirect('dashboard:laporan_daerah', pulau="sumatera selatan")
		        elif request.POST['action'] == 'sumatera_tengah':
		            return redirect('dashboard:laporan_daerah', pulau="sumatera tengah")
		        elif request.POST['action'] == 'sumatera_utara':
		            return redirect('dashboard:laporan_daerah', pulau="sumatera utara")
		        else:
		            return render(request,'sumatera.html',{'username':username,'role':role})
    		        
    		        
		    elif role == 'rsm':
		        if request.POST['action'] == 'lampung_bengkulu':
		            return redirect('dashboard:laporan_daerah', pulau="lampung bengkulu")
		        elif request.POST['action'] == 'sumatera_selatan':
		            return redirect('dashboard:laporan_daerah', pulau="sumatera selatan")
		        elif request.POST['action'] == 'sumatera_tengah':
		            return redirect('dashboard:laporan_daerah', pulau="sumatera tengah")
		        elif request.POST['action'] == 'sumatera_utara':
		            return redirect('dashboard:laporan_daerah', pulau="sumatera utara")
		        else:
		            return render(request,'sumatera.html',{'username':username,'role':role})
    		        
		    elif role == 'am':
		        if request.POST['action'] == 'lampung_bengkulu':
		            return redirect('dashboard:laporan_daerah_am', pulau="lampung bengkulu")
		        elif request.POST['action'] == 'sumatera_selatan':
		            return redirect('dashboard:laporan_daerah_am', pulau="sumatera selatan")
		        elif request.POST['action'] == 'sumatera_tengah':
		            return redirect('dashboard:laporan_daerah_am', pulau="sumatera tengah")
		        elif request.POST['action'] == 'sumatera_utara':
		            return redirect('dashboard:laporan_daerah_am', pulau="sumatera utara")
		        else:
		            return render(request,'sumatera.html',{'username':username,'role':role})
    		        
		else:
			return render(request,'sumatera.html',{'username':username,'role':role})
		
	else:
		return redirect('login:loginPage')

@csrf_exempt
def jawa(request):
	if 'logged_in' in request.session or not request.session['logged_in']:
		cursor = connection.cursor()
		email = request.session['email']
		
		username = request.session['username']
		
		cursor.execute("SELECT role from PROFILE WHERE email = '"+email+"';")
		role = cursor.fetchone()[0]
		cursor.close()

		if request.method == 'POST':
		    if role == 'admin':

		        if request.POST['action'] == 'jawa_timur':
		            return redirect('dashboard:laporan_daerah', pulau="jawa timur")
		        elif request.POST['action'] == 'jawa_tengah':
		            return redirect('dashboard:laporan_daerah', pulau="jawa tengah")
		        elif request.POST['action'] == 'jawa_barat':
		            return redirect('dashboard:laporan_daerah', pulau="jawa barat")
		        else:
		            return render(request,'jawa.html',{'username':username,'role':role})
    		        
		    elif role == 'rsm':
		        if request.POST['action'] == 'jawa_timur':
		            return redirect('dashboard:laporan_daerah', pulau="jawa timur")
		        elif request.POST['action'] == 'jawa_tengah':
		            return redirect('dashboard:laporan_daerah', pulau="jawa tengah")
		        elif request.POST['action'] == 'jawa_barat':
		            return redirect('dashboard:laporan_daerah', pulau="jawa barat")
		        else:
		            return render(request,'jawa.html',{'username':username,'role':role})
    		        
		    elif role == 'am':
		        if request.POST['action'] == 'jawa_timur':
		            return redirect('dashboard:laporan_daerah_am', pulau="jawa timur")
		        elif request.POST['action'] == 'jawa_tengah':
		            return redirect('dashboard:laporan_daerah_am', pulau="jawa tengah")
		        elif request.POST['action'] == 'jawa_barat':
		            return redirect('dashboard:laporan_daerah_am', pulau="jawa barat")
		        else:
		            return render(request,'jawa.html',{'username':username,'role':role})    		        
		else:
			return render(request,'jawa.html',{'username':username,'role':role})


	else:
		return redirect('login:loginPage')

@csrf_exempt
def timur(request):
	if 'logged_in' in request.session or not request.session['logged_in']:
		cursor = connection.cursor()
		email = request.session['email']
		username = request.session['username']
		
		cursor.execute("SELECT role from PROFILE WHERE email = '"+email+"';")
		role = cursor.fetchone()[0]
		cursor.close()

		if request.method == 'POST':
		    if role == 'admin':
		        if request.POST['action'] == 'kalimantan':
		            return redirect('dashboard:laporan_daerah', pulau="kalimantan")
		        elif request.POST['action'] == 'sulawesi':
		            return redirect('dashboard:laporan_daerah', pulau="sulawesi")
		        else:
		            return render(request,'indonesiaTimur.html',{'username':username,'role':role}) 
		            
		    elif role == 'rsm':
		        if request.POST['action'] == 'kalimantan':
		            return redirect('dashboard:laporan_daerah', pulau="kalimantan")
		        elif request.POST['action'] == 'sulawesi':
		            return redirect('dashboard:laporan_daerah', pulau="sulawesi")
		        else:
		            return render(request,'indonesiaTimur.html',{'username':username,'role':role})

		    elif role == 'am':
		        if request.POST['action'] == 'kalimantan':
		            return redirect('dashboard:laporan_daerah_am', pulau="kalimantan")
		        elif request.POST['action'] == 'sulawesi':
		            return redirect('dashboard:laporan_daerah_am', pulau="sulawesi")
		        else:
		            return render(request,'indonesiaTimur.html',{'username':username,'role':role})

		else:
			return render(request,'indonesiaTimur.html',{'username':username,'role':role})
    		        
	else:
		return redirect('login:loginPage')

@csrf_exempt		
def laporan_rsm(request, pulau=False):
    print(settings.DATA_UPLOAD_MAX_MEMORY_SIZE)
    my_date = date.today()
    hari = calendar.day_name[my_date.weekday()]
    d1 = my_date.strftime("%B %d, %Y")
    
    pulau = re.sub(r'%(\d)*', ' ', pulau)
    
    if 'logged_in' not in request.session or not request.session['logged_in']:    
        return redirect('login:loginPage')
    else:
        cursor = connection.cursor()
        email = request.session['email']
        
        cursor.execute("SELECT rsm FROM PROFILE WHERE email = '"+email+"';")
        rsm = cursor.fetchone()
        cursor.execute("SELECT area FROM PROFILE WHERE email = '"+email+"';")
        area = cursor.fetchone()
        if rsm[0] and not area[0]:
            return redirect('login:choose_area')
        elif not rsm[0] and area[0]:
            return redirect('login:choose_rsm')
        elif not rsm[0] and not area[0]:
            return redirect('login:choose_rsm')
        
        searching = False
        menunggu_review = False
        sudah_review = False
        tanggal_terlama = False
        tanggal_tertentu = False
        search_key = False
        
        action_toggle_tanggal = ""
        if request.method == "POST" and request.POST['action'] == "searching":
            print("masuk searching")
            search = request.POST['search']
            search_key = search
            cursor.execute("select L.* from laporan L join profile P on L.email = P.email where (L.email SIMILAR TO '%"+search+"%' OR L.kondisi SIMILAR TO '%"+search+"%' OR L.kompetitor SIMILAR TO '%"+search+"%' OR L.laporan SIMILAR TO '%"+search+"%' OR L.fokus_produk SIMILAR TO '%"+search+"%' OR L.other SIMILAR TO '%"+search+"%') AND P.role = 'rsm' AND P.rsm = '"+pulau+"';")
            
            searching = True
        elif request.method == "POST" and request.POST['action'] == "see-all":
            print("masuk see-all")          
            cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email where P.role = 'rsm' AND P.rsm = '"+pulau+"';")
            
        elif request.method == "POST" and request.POST['action'] == "menunggu-review":
            cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email WHERE (COALESCE(L.is_reviewed, FALSE) = FALSE) AND P.role = 'rsm' AND P.rsm = '"+pulau+"';")
            searching = True
            menunggu_review = True
        elif request.method == "POST" and request.POST['action'] == "sudah-review":            
            cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email WHERE (COALESCE(L.is_reviewed, FALSE) = TRUE) AND P.role = 'rsm' AND P.rsm = '"+pulau+"';") 
            searching = True
            sudah_review = True
        elif request.GET.get('page') is not None:
            print(request.GET.get('page'))
            print(request.GET.get('page').split())
            print(request.GET.get('page').split()[1][16:])
            print(request.GET.get('page').split()[2][13:])
            if request.GET.get('page').split()[1][16:] == "True":
                print("Horay")
                cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email WHERE P.role = 'rsm' AND COALESCE(L.is_reviewed, FALSE) = FALSE AND P.rsm = '"+pulau+"';")
                menunggu_review = True
                searching = True
            elif request.GET.get('page').split()[2][13:] == "True":
                print("Hore!")
                cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email WHERE P.role = 'rsm' AND COALESCE(L.is_reviewed, FALSE) = TRUE AND P.rsm = '"+pulau+"';")
                sudah_review = True
                searching = True
            elif request.GET.get('page').split()[3][16:] == "True":
                cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email WHERE P.role = 'rsm' AND P.rsm = '"+pulau+"' ORDER BY L.waktu ASC ;")
                action_toggle_tanggal = "tanggal-terbaru"
                tanggal_terlama = True
                searching = True
            elif request.GET.get('page').split()[4][17:] != "False":
                tanggal_tertentu = request.GET.get('page').split()[4][17:]
                searching = True
                cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email WHERE P.role = 'rsm' AND P.rsm = '"+pulau+"' AND L.waktu::date = '" + tanggal_tertentu + "' ORDER BY L.waktu ASC;")
            elif request.GET.get('page').split()[5][11:] != "False":
                search_key = request.GET.get('page').split()[5][11:]
                cursor.execute("select L.* from laporan L join profile P on L.email = P.email where (L.email SIMILAR TO '%"+search_key+"%' OR L.kondisi SIMILAR TO '%"+search_key+"%' OR L.kompetitor SIMILAR TO '%"+search_key+"%' OR L.laporan SIMILAR TO '%"+search_key+"%' OR L.fokus_produk SIMILAR TO '%"+search_key+"%' OR L.other SIMILAR TO '%"+search_key+"%') AND P.role = 'rsm' AND P.rsm = '"+pulau+"';") 
                searching = True
                
                
                
                
            else:
                cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email where P.role = 'rsm' AND P.rsm = '"+pulau+"' ORDER BY L.waktu DESC;")
                
        elif request.method == "POST" and request.POST['action'] == "tanggal-terbaru":
            cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email where P.role = 'rsm' AND P.rsm = '"+pulau+"' ORDER BY L.waktu DESC;")
            action_toggle_tanggal = "tanggal-terlama"
        elif request.method == "POST" and request.POST['action'] == "tanggal-terlama":
            cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email where P.role = 'rsm' AND P.rsm = '"+pulau+"' ORDER BY L.waktu ASC;")
            action_toggle_tanggal = "tanggal-terbaru"
            tanggal_terlama = True

        elif request.method == "POST" and request.POST['action'] == "datepicker":
            # print("yay")
            # print("POST:", request.POST['date'])
            tanggal = request.POST['date']
            tanggal_tertentu = tanggal[-4:] + "-" + tanggal[3:5] + "-" + tanggal[0:2]
            if tanggal == "":
                return redirect('dashboard:laporan_rsm',pulau=pulau)
            else:
                cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email where P.role = 'rsm' AND P.rsm = '"+pulau+"' AND L.waktu::date = '" + tanggal_tertentu + "' ORDER BY L.waktu ASC;")
            
        else:
            # print("masuk else")
            cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email where P.role = 'rsm' AND P.rsm = '"+pulau+"' ORDER BY L.waktu DESC;")

        data_query = namedtuplefetchall(cursor)
        cursor.execute("SELECT count(L.*) from laporan L join profile P on L.email = P.email WHERE P.role = 'rsm' AND P.rsm = '"+pulau+"';")

        cursor.execute("SELECT count(L.*) from laporan L join profile P on L.email = P.email WHERE P.role = 'rsm' AND P.rsm = '"+pulau+"' AND COALESCE(L.is_reviewed, FALSE) = TRUE;")
        count_is_reviewed = cursor.fetchone()[0]
        cursor.execute("SELECT count(L.*) from laporan L join profile P on L.email = P.email WHERE P.role = 'rsm' AND P.rsm = '"+pulau+"' AND COALESCE(L.is_reviewed, FALSE) = FALSE;")
        count_is_not_reviewed = cursor.fetchone()[0]

        cursor.execute("SELECT username FROM pengguna WHERE email = '" + email + "';")
        username = cursor.fetchone()[0]

        cursor.execute("SELECT role FROM profile WHERE email = '" + email + "';")
        role = cursor.fetchone()[0]
        data = []
        for item in data_query:
            timestamptz = item[9]
            # print(timestamptz)
            time = timestamptz.strftime("%H:%M")
            timestamp_tanggal = timestamptz.strftime("%A, %d %b %Y")
            # print(time)
            # print(date)
            data.append({'item': item, 'time': time, 'date': timestamp_tanggal})
            
        # paginator = Paginator(data, 5)
        # page_number = request.GET.get('page')
        # page_obj = paginator.get_page(page_number)
        
        # p = Paginator(data, 10)
        # page_number = request.GET.get('page')
        # page_obj = p.get_page(page_number)
        
        p = Paginator(data, 10)
        if request.GET.get('page') is not None:
            page_number = request.GET.get('page').split()[0]
        else:
            page_number = request.GET.get('page')
        page_obj = p.get_page(page_number)
        print(p.num_pages, " - pages!!!!")

        # print(data)
        return render(request, 'laporan_rsm.html', {'rsm':pulau,'data': page_obj,'hari':hari,'tanggal':d1,'toggle_action': action_toggle_tanggal, 'reviewed':count_is_reviewed, 'not_reviewed':count_is_not_reviewed, 'username':username, 'role':role, 'back':searching, "menunggu_review": menunggu_review, "sudah_review": sudah_review, "tanggal_terlama": tanggal_terlama, "tanggal_tertentu": tanggal_tertentu, "search_key": search_key})

@csrf_exempt
def laporan_daerah(request, pulau=False):
    
    print(settings.DATA_UPLOAD_MAX_MEMORY_SIZE)
    my_date = date.today()
    hari = calendar.day_name[my_date.weekday()]
    d1 = my_date.strftime("%B %d, %Y")
    
    pulau = re.sub(r'%(\d)*', ' ', pulau)
    
    if 'logged_in' not in request.session or not request.session['logged_in']:    
        return redirect('login:loginPage')
    else:
        cursor = connection.cursor()
        email = request.session['email']
        
        cursor.execute("SELECT rsm FROM PROFILE WHERE email = '"+email+"';")
        rsm = cursor.fetchone()
        cursor.execute("SELECT area FROM PROFILE WHERE email = '"+email+"';")
        area = cursor.fetchone()
        if rsm[0] and not area[0]:
            return redirect('login:choose_area')
        elif not rsm[0] and area[0]:
            return redirect('login:choose_rsm')
        elif not rsm[0] and not area[0]:
            return redirect('login:choose_rsm')
        
        searching = False
        menunggu_review = False
        sudah_review = False
        tanggal_terlama = False
        tanggal_tertentu = False
        search_key = False
        
        action_toggle_tanggal = ""
        if request.method == "POST" and request.POST['action'] == "searching":
            print("masuk searching")
            search = request.POST['search']
            search_key = search
            cursor.execute("select L.* from laporan L join profile P on L.email = P.email where (L.email SIMILAR TO '%"+search+"%' OR L.kondisi SIMILAR TO '%"+search+"%' OR L.kompetitor SIMILAR TO '%"+search+"%' OR L.laporan SIMILAR TO '%"+search+"%' OR L.fokus_produk SIMILAR TO '%"+search+"%' OR L.other SIMILAR TO '%"+search+"%') AND (P.role = 'am' OR P.role = 'karyawan') AND P.area = '"+pulau+"';")
            
            searching = True
        elif request.method == "POST" and request.POST['action'] == "see-all":
            print("masuk see-all")          
            cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email where (P.role = 'am' OR P.role = 'karyawan') AND P.area = '"+pulau+"';")
            
        elif request.method == "POST" and request.POST['action'] == "menunggu-review":
            cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email WHERE (COALESCE(L.is_reviewed, FALSE) = FALSE) AND (P.role = 'am' OR P.role = 'karyawan') AND P.area = '"+pulau+"';")
            searching = True
            menunggu_review = True
        elif request.method == "POST" and request.POST['action'] == "sudah-review":            
            cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email WHERE (COALESCE(L.is_reviewed, FALSE) = TRUE) AND (P.role = 'am' OR P.role = 'karyawan') AND P.area = '"+pulau+"';") 
            searching = True
            sudah_review = True
        elif request.GET.get('page') is not None:
            print(request.GET.get('page'))
            print(request.GET.get('page').split())
            print(request.GET.get('page').split()[1][16:])
            print(request.GET.get('page').split()[2][13:])
            if request.GET.get('page').split()[1][16:] == "True":
                print("Horay")
                cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email WHERE (P.role = 'am' OR P.role = 'karyawan') AND COALESCE(L.is_reviewed, FALSE) = FALSE AND P.area = '"+pulau+"';")
                menunggu_review = True
                searching = True
            elif request.GET.get('page').split()[2][13:] == "True":
                print("Hore!")
                cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email WHERE (P.role = 'am' OR P.role = 'karyawan') AND COALESCE(L.is_reviewed, FALSE) = TRUE AND P.area = '"+pulau+"';")
                sudah_review = True
                searching = True
            elif request.GET.get('page').split()[3][16:] == "True":
                cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email WHERE (P.role = 'am' OR P.role = 'karyawan') AND P.area = '"+pulau+"' ORDER BY L.waktu ASC ;")
                action_toggle_tanggal = "tanggal-terbaru"
                tanggal_terlama = True
                searching = True
            elif request.GET.get('page').split()[4][17:] != "False":
                tanggal_tertentu = request.GET.get('page').split()[4][17:]
                searching = True
                cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email WHERE (P.role = 'am' OR P.role = 'karyawan') AND P.area = '"+pulau+"' AND L.waktu::date = '" + tanggal_tertentu + "' ORDER BY L.waktu ASC;")
            elif request.GET.get('page').split()[5][11:] != "False":
                search_key = request.GET.get('page').split()[5][11:]
                cursor.execute("select L.* from laporan L join profile P on L.email = P.email where (L.email SIMILAR TO '%"+search_key+"%' OR L.kondisi SIMILAR TO '%"+search_key+"%' OR L.kompetitor SIMILAR TO '%"+search_key+"%' OR L.laporan SIMILAR TO '%"+search_key+"%' OR L.fokus_produk SIMILAR TO '%"+search_key+"%' OR L.other SIMILAR TO '%"+search_key+"%') AND (P.role = 'am' OR P.role = 'karyawan') AND P.area = '"+pulau+"';") 
                searching = True
                
                
                
                
            else:
                cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email where (P.role = 'am' OR P.role = 'karyawan') AND P.area = '"+pulau+"' ORDER BY L.waktu DESC;")
                
        elif request.method == "POST" and request.POST['action'] == "tanggal-terbaru":
            cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email where (P.role = 'am' OR P.role = 'karyawan') AND P.area = '"+pulau+"' ORDER BY L.waktu DESC;")
            action_toggle_tanggal = "tanggal-terlama"
        elif request.method == "POST" and request.POST['action'] == "tanggal-terlama":
            cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email where (P.role = 'am' OR P.role = 'karyawan') AND P.area = '"+pulau+"' ORDER BY L.waktu ASC;")
            action_toggle_tanggal = "tanggal-terbaru"
            tanggal_terlama = True

        elif request.method == "POST" and request.POST['action'] == "datepicker":
            # print("yay")
            # print("POST:", request.POST['date'])
            tanggal = request.POST['date']
            tanggal_tertentu = tanggal[-4:] + "-" + tanggal[3:5] + "-" + tanggal[0:2]
            if tanggal == "":
                return redirect('dashboard:laporan_daerah',pulau=pulau)
            else:
                cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email where (P.role = 'am' OR P.role = 'karyawan') AND P.area = '"+pulau+"' AND L.waktu::date = '" + tanggal_tertentu + "' ORDER BY L.waktu ASC;")
            
        else:
            # print("masuk else")
            cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email where (P.role = 'am' OR P.role = 'karyawan') AND P.area = '"+pulau+"' ORDER BY L.waktu DESC;")

        data_query = namedtuplefetchall(cursor)
        cursor.execute("SELECT count(L.*) from laporan L join profile P on L.email = P.email WHERE (P.role = 'am' OR P.role = 'karyawan') AND P.area = '"+pulau+"';")

        cursor.execute("SELECT count(L.*) from laporan L join profile P on L.email = P.email WHERE (P.role = 'am' OR P.role = 'karyawan') AND P.area = '"+pulau+"' AND COALESCE(L.is_reviewed, FALSE) = TRUE;")
        count_is_reviewed = cursor.fetchone()[0]
        cursor.execute("SELECT count(L.*) from laporan L join profile P on L.email = P.email WHERE (P.role = 'am' OR P.role = 'karyawan') AND P.area = '"+pulau+"' AND COALESCE(L.is_reviewed, FALSE) = FALSE;")
        count_is_not_reviewed = cursor.fetchone()[0]

        cursor.execute("SELECT username FROM pengguna WHERE email = '" + email + "';")
        username = cursor.fetchone()[0]

        cursor.execute("SELECT role FROM profile WHERE email = '" + email + "';")
        role = cursor.fetchone()[0]
        data = []
        for item in data_query:
            timestamptz = item[9]
            # print(timestamptz)
            time = timestamptz.strftime("%H:%M")
            timestamp_tanggal = timestamptz.strftime("%A, %d %b %Y")
            # print(time)
            # print(date)
            data.append({'item': item, 'time': time, 'date': timestamp_tanggal})
            
        # paginator = Paginator(data, 5)
        # page_number = request.GET.get('page')
        # page_obj = paginator.get_page(page_number)
        
        # p = Paginator(data, 10)
        # page_number = request.GET.get('page')
        # page_obj = p.get_page(page_number)
        
        p = Paginator(data, 10)
        if request.GET.get('page') is not None:
            page_number = request.GET.get('page').split()[0]
        else:
            page_number = request.GET.get('page')
        page_obj = p.get_page(page_number)
        print(p.num_pages, " - pages!!!!")

        # print(data)
        return render(request, 'laporan_daerah.html', {'rsm':pulau,'data': page_obj,'hari':hari,'tanggal':d1,'toggle_action': action_toggle_tanggal, 'reviewed':count_is_reviewed, 'not_reviewed':count_is_not_reviewed, 'username':username, 'role':role, 'back':searching, "menunggu_review": menunggu_review, "sudah_review": sudah_review, "tanggal_terlama": tanggal_terlama, "tanggal_tertentu": tanggal_tertentu, "search_key": search_key})

@csrf_exempt
def laporan_daerah_am(request, pulau=False):
    print(settings.DATA_UPLOAD_MAX_MEMORY_SIZE)
    my_date = date.today()
    hari = calendar.day_name[my_date.weekday()]
    d1 = my_date.strftime("%B %d, %Y")
    
    pulau = re.sub(r'%(\d)*', ' ', pulau)
    
    if 'logged_in' not in request.session or not request.session['logged_in']:    
        return redirect('login:loginPage')
    else:
        cursor = connection.cursor()
        email = request.session['email']
        
        cursor.execute("SELECT rsm FROM PROFILE WHERE email = '"+email+"';")
        rsm = cursor.fetchone()
        cursor.execute("SELECT area FROM PROFILE WHERE email = '"+email+"';")
        area = cursor.fetchone()
        if rsm[0] and not area[0]:
            return redirect('login:choose_area')
        elif not rsm[0] and area[0]:
            return redirect('login:choose_rsm')
        elif not rsm[0] and not area[0]:
            return redirect('login:choose_rsm')
        
        searching = False
        menunggu_review = False
        sudah_review = False
        tanggal_terlama = False
        tanggal_tertentu = False
        search_key = False
        
        action_toggle_tanggal = ""
        if request.method == "POST" and request.POST['action'] == "searching":
            print("masuk searching")
            search = request.POST['search']
            search_key = search
            cursor.execute("select L.* from laporan L join profile P on L.email = P.email where (L.email SIMILAR TO '%"+search+"%' OR L.kondisi SIMILAR TO '%"+search+"%' OR L.kompetitor SIMILAR TO '%"+search+"%' OR L.laporan SIMILAR TO '%"+search+"%' OR L.fokus_produk SIMILAR TO '%"+search+"%' OR L.other SIMILAR TO '%"+search+"%') AND (P.role = 'karyawan') AND P.area = '"+pulau+"';")
            
            searching = True
        elif request.method == "POST" and request.POST['action'] == "see-all":
            print("masuk see-all")          
            cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email where (P.role = 'karyawan') AND P.area = '"+pulau+"';")
            
        elif request.method == "POST" and request.POST['action'] == "menunggu-review":
            cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email WHERE (COALESCE(L.is_reviewed, FALSE) = FALSE) AND (P.role = 'karyawan') AND P.area = '"+pulau+"';")
            searching = True
            menunggu_review = True
        elif request.method == "POST" and request.POST['action'] == "sudah-review":            
            cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email WHERE (COALESCE(L.is_reviewed, FALSE) = TRUE) AND (P.role = 'karyawan') AND P.area = '"+pulau+"';") 
            searching = True
            sudah_review = True
        elif request.GET.get('page') is not None:
            print(request.GET.get('page'))
            print(request.GET.get('page').split())
            print(request.GET.get('page').split()[1][16:])
            print(request.GET.get('page').split()[2][13:])
            if request.GET.get('page').split()[1][16:] == "True":
                print("Horay")
                cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email WHERE (OR P.role = 'karyawan') AND COALESCE(L.is_reviewed, FALSE) = FALSE AND P.area = '"+pulau+"';")
                menunggu_review = True
                searching = True
            elif request.GET.get('page').split()[2][13:] == "True":
                print("Hore!")
                cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email WHERE (P.role = 'karyawan') AND COALESCE(L.is_reviewed, FALSE) = TRUE AND P.area = '"+pulau+"';")
                sudah_review = True
                searching = True
            elif request.GET.get('page').split()[3][16:] == "True":
                cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email WHERE (P.role = 'karyawan') AND P.area = '"+pulau+"' ORDER BY L.waktu ASC ;")
                action_toggle_tanggal = "tanggal-terbaru"
                tanggal_terlama = True
                searching = True
            elif request.GET.get('page').split()[4][17:] != "False":
                tanggal_tertentu = request.GET.get('page').split()[4][17:]
                searching = True
                cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email WHERE (P.role = 'karyawan') AND P.area = '"+pulau+"' AND L.waktu::date = '" + tanggal_tertentu + "' ORDER BY L.waktu ASC;")
            elif request.GET.get('page').split()[5][11:] != "False":
                search_key = request.GET.get('page').split()[5][11:]
                cursor.execute("select L.* from laporan L join profile P on L.email = P.email where (L.email SIMILAR TO '%"+search_key+"%' OR L.kondisi SIMILAR TO '%"+search_key+"%' OR L.kompetitor SIMILAR TO '%"+search_key+"%' OR L.laporan SIMILAR TO '%"+search_key+"%' OR L.fokus_produk SIMILAR TO '%"+search_key+"%' OR L.other SIMILAR TO '%"+search_key+"%') AND (P.role = 'karyawan') AND P.area = '"+pulau+"';") 
                searching = True
                
                
                
                
            else:
                cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email where (P.role = 'karyawan') AND P.area = '"+pulau+"' ORDER BY L.waktu DESC;")
                
        elif request.method == "POST" and request.POST['action'] == "tanggal-terbaru":
            cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email where (P.role = 'karyawan') AND P.area = '"+pulau+"' ORDER BY L.waktu DESC;")
            action_toggle_tanggal = "tanggal-terlama"
        elif request.method == "POST" and request.POST['action'] == "tanggal-terlama":
            cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email where (P.role = 'karyawan') AND P.area = '"+pulau+"' ORDER BY L.waktu ASC;")
            action_toggle_tanggal = "tanggal-terbaru"
            tanggal_terlama = True

        elif request.method == "POST" and request.POST['action'] == "datepicker":
            # print("yay")
            # print("POST:", request.POST['date'])
            tanggal = request.POST['date']
            tanggal_tertentu = tanggal[-4:] + "-" + tanggal[3:5] + "-" + tanggal[0:2]
            if tanggal == "":
                return redirect('dashboard:laporan_daerah_am',pulau=pulau)
            else:
                cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email where (P.role = 'karyawan') AND P.area = '"+pulau+"' AND L.waktu::date = '" + tanggal_tertentu + "' ORDER BY L.waktu ASC;")
            
        else:
            # print("masuk else")
            cursor.execute("SELECT L.* from laporan L join profile P on L.email = P.email where (P.role = 'karyawan') AND P.area = '"+pulau+"' ORDER BY L.waktu DESC;")

        data_query = namedtuplefetchall(cursor)
        cursor.execute("SELECT count(L.*) from laporan L join profile P on L.email = P.email WHERE (P.role = 'karyawan') AND P.area = '"+pulau+"';")

        cursor.execute("SELECT count(L.*) from laporan L join profile P on L.email = P.email WHERE (P.role = 'karyawan') AND P.area = '"+pulau+"' AND COALESCE(L.is_reviewed, FALSE) = TRUE;")
        count_is_reviewed = cursor.fetchone()[0]
        cursor.execute("SELECT count(L.*) from laporan L join profile P on L.email = P.email WHERE (P.role = 'karyawan') AND P.area = '"+pulau+"' AND COALESCE(L.is_reviewed, FALSE) = FALSE;")
        count_is_not_reviewed = cursor.fetchone()[0]

        cursor.execute("SELECT username FROM pengguna WHERE email = '" + email + "';")
        username = cursor.fetchone()[0]

        cursor.execute("SELECT role FROM profile WHERE email = '" + email + "';")
        role = cursor.fetchone()[0]
        data = []
        for item in data_query:
            timestamptz = item[9]
            # print(timestamptz)
            time = timestamptz.strftime("%H:%M")
            timestamp_tanggal = timestamptz.strftime("%A, %d %b %Y")
            # print(time)
            # print(date)
            data.append({'item': item, 'time': time, 'date': timestamp_tanggal})
            
        # paginator = Paginator(data, 5)
        # page_number = request.GET.get('page')
        # page_obj = paginator.get_page(page_number)
        
        # p = Paginator(data, 10)
        # page_number = request.GET.get('page')
        # page_obj = p.get_page(page_number)
        
        p = Paginator(data, 10)
        if request.GET.get('page') is not None:
            page_number = request.GET.get('page').split()[0]
        else:
            page_number = request.GET.get('page')
        page_obj = p.get_page(page_number)
        print(p.num_pages, " - pages!!!!")

        # print(data)
        return render(request, 'laporan_daerah_am.html', {'rsm':pulau,'data': page_obj,'hari':hari,'tanggal':d1,'toggle_action': action_toggle_tanggal, 'reviewed':count_is_reviewed, 'not_reviewed':count_is_not_reviewed, 'username':username, 'role':role, 'back':searching, "menunggu_review": menunggu_review, "sudah_review": sudah_review, "tanggal_terlama": tanggal_terlama, "tanggal_tertentu": tanggal_tertentu, "search_key": search_key})

@csrf_exempt
def pilih_user(request):
    if 'logged_in' not in request.session or not request.session['logged_in']:    
        return redirect('login:loginPage')
    else:
        cursor = connection.cursor()
        search_keyword = False
        
        if request.method == "POST":
            search_keyword = request.POST['search_keyword']
            cursor.execute("SELECT foto_profile, nama_lengkap, email, no_hp, role, rsm, area FROM profile WHERE (email LIKE '%" + search_keyword + "%' OR nama_lengkap LIKE '%" + search_keyword + "%') AND email!='" + request.session['email'] + "';")
            
        elif request.GET.get('page') is not None:
            
            if request.GET.get('page').split()[1][15:] != "False":
                search_keyword = request.GET.get('page').split()[1][15:]
                cursor.execute("SELECT foto_profile, nama_lengkap, email, no_hp, role, rsm, area FROM profile WHERE (email LIKE '%" + search_keyword + "%' OR nama_lengkap LIKE '%" + search_keyword + "%') AND email!='" + request.session['email'] + "';")
                # searching = True
            else:
                cursor.execute("SELECT foto_profile, nama_lengkap, email, no_hp, role, rsm, area FROM profile WHERE email!='" + request.session['email'] + "';")
        else:
            cursor.execute("SELECT foto_profile, nama_lengkap, email, no_hp, role, rsm, area FROM profile WHERE email!='" + request.session['email'] + "';")
        
        data = []
        data_query = namedtuplefetchall(cursor)
        for item in data_query:
            foto_profile = item[0]
            if foto_profile:
                foto_profile = foto_profile[34:]
                
            data.append({'pengguna': item, 'foto_profile': foto_profile})
            
        p = Paginator(data, 10)
        if request.GET.get('page') is not None:
            page_number = request.GET.get('page').split()[0]
        else:
            page_number = request.GET.get('page')
        page_obj = p.get_page(page_number)
        return render(request, 'pilih_user.html', {'data':page_obj, 'search_keyword': search_keyword})

@csrf_exempt		
def ganti_jabatan(request, email):
    if 'logged_in' not in request.session or not request.session['logged_in']:    
        return redirect('login:loginPage')
    else:
        cursor = connection.cursor()
        success = "False"
        
        if request.method == "POST":
            area_di_sumatera = ["sumatera selatan", "lampung bengkulu", "sumatera tengah", "sumatera utara"]
            area_di_jawa = ["jawa timur", "jawa tengah", "jawa barat"]
            area_di_indonesia_timur = ["sulawesi", "kalimantan"]
            
            post_split = request.POST["jabatan"].split("_")
            role = post_split[0]
            location = ""
            rsm_or_area = "False"
            if len(post_split) == 2:
                rsm_or_area = True
                location = post_split[1]
                
            if role == "rsm":
                cursor.execute("UPDATE profile set rsm = '" + location + "', role = 'rsm', area=NULL where email = '"+email+"';")
                success = "True"
            elif role == "am":
                if location in area_di_sumatera:
                    cursor.execute("UPDATE profile set area = '" + location + "', role = 'am', rsm='sumatera' where email = '"+email+"';")    
                    success = "True"
                elif location in area_di_jawa:
                    cursor.execute("UPDATE profile set area = '" + location + "', role = 'am', rsm='jawa' where email = '"+email+"';")    
                    success = "True"
                elif location in area_di_indonesia_timur:
                    cursor.execute("UPDATE profile set area = '" + location + "', role = 'am', rsm='indonesia timur' where email = '"+email+"';")    
                    success = "True"
                
            elif role == "karyawan":
                cursor.execute("UPDATE profile set role = 'karyawan', rsm=NULL, area=NULL where email = '"+email+"';")
                success = "True"
                
                
        
        cursor.execute("SELECT foto_profile, nama_lengkap, email, no_hp, role, rsm, area, alamat, jabatan, nama_atasan FROM profile WHERE email='" + email + "';")
        data = namedtuplefetchall(cursor)[0]
        foto_profile = data[0]
        if data[0]:
            foto_profile = data[0][34:]
        return render(request, 'ganti_jabatan.html', {"data": data, "foto_profile": foto_profile, "success": success})


def error_404(request):
    return render(request, "404.html")
    
def error_403(request, *args, **argv):
    return render(request, "403.html")



        


        



