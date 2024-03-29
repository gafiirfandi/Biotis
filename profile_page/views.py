from django.shortcuts import render, redirect
from collections import namedtuple
from django.db import connection
from .forms import FormProfile
import PIL
from PIL import Image
from django.views.decorators.csrf import csrf_exempt
import os
from io import BytesIO
import base64
import re
import pathlib
from django.core.files.storage import default_storage
from django.conf import settings



def pil2datauri(img):
    #converts PIL image to datauri
    data = BytesIO()
    img.save(data, "JPEG")
    data64 = base64.b64encode(data.getvalue())
    return u'data:img/jpeg;base64,'+data64.decode('utf-8')

def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

@csrf_exempt
def editprofile(request):
    
    
    
    if 'logged_in' not in request.session or not request.session['logged_in']:
        return redirect('login:loginPage')
    else:
        cursor = connection.cursor()
        email = request.session['email']
        if request.method == 'POST':   
            imageDataURL = request.POST['imageDataURL']
            extension = ''
            if 'data:image/png;' in imageDataURL:
                extension = 'png'
            elif 'data:image/jpg' in imageDataURL:
                extension = 'jpg'
            elif 'data:image/jpeg' in imageDataURL:
                extension = 'jpg'
            else:
                imageDataURL = ''
    
            path = ""
            if imageDataURL != "":
                image_data = re.sub('^data:image/.+;base64,', '', imageDataURL)
                im1 = Image.open(BytesIO(base64.b64decode(image_data)))
                profile_pic_path = '/static/img/user/'
                path = '/home/biotisst/public_html' + profile_pic_path + email
                if not(os.path.isdir(path)):
                    os.mkdir(path)
                path += '/profile'
                if not(os.path.isdir(path)):
                    os.mkdir(path)
                path += '/profile.'+extension

                if extension == 'png':
                    im1 = im1.convert('RGB')

                print(im1)

                im1 = im1.save(path)
                

            nama_lengkap = request.POST.get("nama_lengkap")
            no_hp = request.POST.get("no_hp")
            alamat = request.POST.get("alamat")
            jabatan = request.POST.get("jabatan")
            nama_atasan = request.POST.get("nama_atasan")

            if nama_lengkap == "":
                cursor.execute("SELECT nama_lengkap FROM profile where email = '"+email+"';")
                nama_lengkap = cursor.fetchone()[0]

            if no_hp == "":
                cursor.execute("SELECT no_hp FROM profile where email = '"+email+"';")
                no_hp = cursor.fetchone()[0]

            if alamat == "":
                cursor.execute("SELECT alamat FROM profile where email = '"+email+"';")
                alamat = cursor.fetchone()[0]

            if jabatan == "":
                cursor.execute("SELECT jabatan FROM profile where email = '"+email+"';")
                jabatan = cursor.fetchone()[0]

            if nama_atasan == "":
                cursor.execute("SELECT nama_atasan FROM profile where email = '"+email+"';")
                nama_atasan = cursor.fetchone()[0]
            
            if path == "":
                update_sql = "UPDATE profile set nama_lengkap = %s, no_hp = %s, alamat = %s, jabatan = %s, nama_atasan = %s WHERE email = '"+email+"';"
                record_to_update = [(nama_lengkap, no_hp, alamat, jabatan, nama_atasan)]
                cursor.executemany(update_sql, record_to_update)
            else :
                update_sql = "UPDATE profile set nama_lengkap = %s, no_hp = %s, alamat = %s, jabatan = %s, nama_atasan = %s, foto_profile = %s WHERE email = '"+email+"';"
                record_to_update = [(nama_lengkap, no_hp, alamat, jabatan, nama_atasan, path)]
                cursor.executemany(update_sql, record_to_update)

            return redirect("profile:profile")
        else:
            form = FormProfile()
            cursor.execute("SELECT foto_profile FROM PROFILE WHERE email = '"+email+"';")
            foto_profile = cursor.fetchone()

            cursor.execute("SELECT * FROM profile WHERE email = '"+email+"';")
            data_user = namedtuplefetchall(cursor)[0]

            form.fields['nama_lengkap'].initial = data_user.nama_lengkap
            form.fields['no_hp'].initial = data_user.no_hp
            form.fields['alamat'].initial = data_user.alamat
            form.fields['jabatan'].initial = data_user.jabatan
            form.fields['nama_atasan'].initial = data_user.nama_atasan
            

            data_url_bool = False
            if foto_profile[0] != None:
                img = Image.open(foto_profile[0])
                foto_profile = pil2datauri(img)
                data_url_bool = True
            
                

            
            return render(request, 'edit_profile.html', {'form':form, 'email':email, 'foto_profile':foto_profile, 'data_url':data_url_bool})

def profile(request):
    if 'logged_in' not in request.session or not request.session['logged_in']:
        return redirect('login:loginPage')
    else:

        email = request.session['email'] 
        cursor = connection.cursor()
        cursor.execute("SELECT username FROM PENGGUNA WHERE email = '"+email+"';")
        username = cursor.fetchone()
        cursor.execute("SELECT nama_lengkap FROM PROFILE WHERE email = '"+email+"';")
        nama_lengkap = cursor.fetchone()
        cursor.execute("SELECT no_hp FROM PROFILE WHERE email = '"+email+"';")
        no_hp = cursor.fetchone()
        cursor.execute("SELECT alamat FROM PROFILE WHERE email = '"+email+"';")
        alamat = cursor.fetchone()
        cursor.execute("SELECT jabatan FROM PROFILE WHERE email = '"+email+"';")
        jabatan = cursor.fetchone()
        cursor.execute("SELECT nama_atasan FROM PROFILE WHERE email = '"+email+"';")
        nama_atasan = cursor.fetchone()
        cursor.execute("SELECT role FROM PROFILE WHERE email = '"+email+"';")
        role = cursor.fetchone()
        cursor.execute("SELECT foto_profile FROM PROFILE WHERE email = '"+email+"';")
        foto_profile = cursor.fetchone()

        
        data_url_bool = False
        if foto_profile[0] != None:
            img = Image.open(foto_profile[0])
            foto_profile = pil2datauri(img)
            data_url_bool = True
    

        return render(request, 'profile.html', {'username':username[0], 'email':email, 'nama_lengkap':nama_lengkap[0], 'no_hp':no_hp[0], 
        'alamat':alamat[0], 'jabatan':jabatan[0], 'nama_atasan':nama_atasan[0], 'role':role[0], 'foto_profile':foto_profile, 'data_url':data_url_bool})