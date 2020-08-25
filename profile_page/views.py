from django.shortcuts import render, redirect
from collections import namedtuple
from django.db import connection
from .forms import FormProfile


def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def editprofile(request):
    cursor = connection.cursor()
    email = request.session['email']
    if 'logged_in' not in request.session or not request.session['logged_in']:
        return redirect('login:loginPage')
    else:
        if request.method == 'POST':
        
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

            update_sql = "UPDATE profile set nama_lengkap = %s, no_hp = %s, alamat = %s, jabatan = %s, nama_atasan = %s WHERE email = '"+email+"';"
            record_to_update = [(nama_lengkap, no_hp, alamat, jabatan, nama_atasan)]
            cursor.executemany(update_sql, record_to_update)
            
            return redirect("profile:profile")
        else:
            form = FormProfile()
            
            return render(request, 'edit_profile.html', {'form':form, 'email':email})

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


        return render(request, 'profile.html', {'username':username[0], 'email':email, 'nama_lengkap':nama_lengkap[0], 'no_hp':no_hp[0], 
        'alamat':alamat[0], 'jabatan':jabatan[0], 'nama_atasan':nama_atasan[0], 'role':role[0]})