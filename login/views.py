from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from .forms import CreateUserForm, Login, Reset
from collections import namedtuple
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from biotis import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


UserModel = get_user_model()
user_data = ['default', 'default', 'default']

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
			if form.is_valid():
				
				email = request.POST['email']
				username = request.POST['username']
				password = request.POST['password1']
				user_data[0] = email
				user_data[1] = username
				user_data[2] = password
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
					user = form.save(commit=False)
					user.is_active = False
					user.save()
					current_site = get_current_site(request)
					mail_subject = 'Activate your account.'
					message = render_to_string('accounts/acc_active_email.html', {
						'user' : user,
						'domain' : current_site.domain,
						'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
						'token' : default_token_generator.make_token(user),
					})
					to_email = email
					email_send = EmailMessage(
						mail_subject, message, settings.EMAIL_HOST_USER, [to_email]
					)
					email_send.fail_silently = False
					email_send.send()
					return render (request, 'response.html')
					# cursor.execute("INSERT INTO pengguna (email, username, password) VALUES"
					# 				"('"+email+"', '"+username+"', '"+password+"');")
					# cursor.execute("INSERT INTO profile (email, role) VALUES"
					# 				"('"+email+"', 'karyawan');")
					# request.session["email"] = email
					# request.session["username"] = username
					# request.session["role"] = "karyawan"
					# request.session["password1"] = password
					# request.session["logged_in"] = True
					# request.session.modified = True
					# cursor.close()
					# return redirect ('dashboard:dashboard')
		
		else:
			form = CreateUserForm()
		return render (request , 'register.html' , {'form' : form} )

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

					cursor.execute("SELECT role FROM PROFILE WHERE email = '" + select[0] + "';")
					role = cursor.fetchone()
					request.session['role'] = role[0]
					
					
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


def activate(request, uidb64, token):
	try:
		uid = urlsafe_base64_decode(uidb64).decode()
		user = UserModel._default_manager.get(pk=uid)
	except(TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None
	if user is not None and default_token_generator.check_token(user, token):
		user.is_active = True
		cursor = connection.cursor()
		print(user_data[0])
		cursor.execute("INSERT INTO pengguna (email, username, password) VALUES"
						"('"+user_data[0]+"', '"+user_data[1]+"', '"+user_data[2]+"');")
		cursor.execute("INSERT INTO profile (email, role) VALUES"
						"('"+user_data[0]+"', 'karyawan');")
		request.session["email"] = user_data[0]
		request.session["username"] = user_data[1]
		request.session["role"] = "karyawan"
		request.session["password1"] = user_data[2]
		request.session["logged_in"] = True
		request.session.modified = True
		cursor.close()
		user.save()
		return render (request, 'verification.html')
	else:
		return HttpResponse('Activation link is invalid!')

def reset(request):
	if 'logged_in' not in request.session or not request.session['logged_in']:
		cursor = connection.cursor()
		if request.method == 'POST':
			email = request.POST['email']
			password = request.POST['password']
			cursor.execute("SELECT * FROM PENGGUNA WHERE email = '"+email+"';")
			select = cursor.fetchone()
			if(select):
				cursor.execute("UPDATE PENGGUNA set password = '"+password+"' where email = '"+email+"';")
				request.session.modified = True
				
				cursor.close()
				return redirect('login:loginPage')

			else:
				messages.error(request, 'Email Not Exist.')
				form = Reset()
				

		else:
			form = Reset()
		return render(request, 'reset.html', {'form':form})


	else:
		return redirect('dashboard:dashboard')


