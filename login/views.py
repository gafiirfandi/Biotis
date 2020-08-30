from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from .forms import CreateUserForm, Login
from collections import namedtuple

def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

@csrf_exempt
def registerPage(request):
	if 'logged_in' not in request.session or not request.session['logged_in']:
		cursor = connection.cursor()
		if request.method == 'POST':
			form = CreateUserForm(request.POST)
			email = request.POST['email']
			username = request.POST['username']
			password = request.POST['password']
			cursor.execute("SELECT * from pengguna where email = '"+email+"';")
			select = cursor.fetchone()
			cursor.execute("SELECT * from pengguna where username = '"+username+"';")
			select2 = cursor.fetchone()
			if (select):
				messages.error(request, 'Email Already Registered.')
				return redirect('login:loginPage')
			elif(select2):
				messages.error(request, 'Username Already Registered.')
				return redirect('login:register')
			else:
				cursor.execute("INSERT INTO pengguna (email, username, password) VALUES"
								"('"+email+"', '"+username+"', '"+password+"');")
				cursor.execute("INSERT INTO profile (email, role) VALUES"
								"('"+email+"', 'karyawan');")
				request.session["email"] = email
				request.session["username"] = username
				request.session["role"] = "karyawan"
				request.session["password"] = password
				request.session["logged_in"] = True
				request.session.modified = True
				cursor.close()
				return redirect ('dashboard:dashboard')
		else:
			form = CreateUserForm()
			context = {'form' : form}
			return render (request , 'register.html' , context )

	else:
		return redirect('login:loginPage')


def loginPage(request):
	if 'logged_in' not in request.session or not request.session['logged_in']:
		cursor = connection.cursor()
		if request.method == 'POST':
			username = request.POST['username']
			password = request.POST['password']
			cursor.execute("SELECT * FROM PENGGUNA WHERE username = '"+username+"';")
			select = cursor.fetchone()
			if(select):
				cursor.execute("SELECT password FROM PENGGUNA WHERE username = '"+username+"';")
				select = cursor.fetchone()
				if(select[0] == password):
					request.session['logged_in'] = True
					request.session.modified = True
					request.session['password'] = select[0]

					cursor.execute("SELECT email FROM PENGGUNA WHERE username = '"+username+"';")
					select = cursor.fetchone()
					request.session['email'] = select[0]
					request.session['username'] = username
					
					cursor.close()
					return redirect('dashboard:dashboard')
				
				else:
					form = Login()
					return render(request, 'login.html', {'form':form})

			else:
				form = Login()
				return render(request, 'login.html', {'form':form})

		else:
			form = Login()
			return render(request, 'login.html', {'form':form})


	else:
		return redirect('dashboard:dashboard')



def logoutUser(request):
	request.session.flush()
	return redirect('login:loginPage')