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
from django.contrib.auth.models import User


UserModel = get_user_model()
user_data = ['default', 'default', 'default']

def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

@csrf_exempt
def registerPage(request, valid=True):
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
				select = cursor.fetchall()
				cursor.execute("SELECT * from pengguna where username = '"+username+"';")
				select2 = cursor.fetchall()
				if (select):
					return redirect('login:valid')
				elif(select2):
					messages.error(request, 'Username Already Registered.')
					return redirect('login:valid')
				else:
				    try:
				        user_exist = User.objects.get(email=email)
				        
				        return redirect('login:email')
				    except User.DoesNotExist:
    					user = form.save(commit=False)
    					user.is_active = False
    					user.save()
    					request.session["email"] = email
    					request.session["username"] = username
    					request.session["password1"] = password
    					current_site = get_current_site(request)
    					cursor.execute("INSERT INTO pengguna (email, username, password) VALUES ('"+email+"', '"+username+"', '"+password+"');")
    					cursor.execute("INSERT INTO profile (email, role) VALUES ('"+email+"', 'karyawan');")
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
    					return redirect('login:verification')
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

@csrf_exempt
def loginPage(request):
	if 'logged_in' not in request.session or not request.session['logged_in']:
		cursor = connection.cursor()
		if request.method == 'POST':
			username = request.POST['username']
			password = request.POST['password']
			cursor.execute("SELECT * FROM PENGGUNA WHERE username = '"+username+"';")
			select = cursor.fetchall()
			cursor.execute("SELECT regis FROM PENGGUNA WHERE username = '"+username+"';")
			regis = cursor.fetchall()
			if(select and regis):
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
					
					email = request.session['email']

					cursor.execute("SELECT role FROM PROFILE WHERE email = '" + select[0] + "';")
					role = cursor.fetchone()
					request.session['role'] = role[0]
					
					cursor.execute("SELECT rsm FROM PROFILE WHERE email = '"+email+"';")
					rsm = cursor.fetchone()
					
					cursor.execute("SELECT area FROM PROFILE WHERE email = '"+email+"';")
					area = cursor.fetchone()
					
					cursor.close()
					if rsm[0] and not area[0]:
					    if rsm[0] == 'indonesia timur':
					        request.session['rsm'] = 'timur'
					    else:
					        request.session['rsm'] = rsm[0]
					    return redirect('login:choose_area')
					elif not rsm[0] and area[0]:
						return redirect('login:choose_rsm')
					elif not rsm[0] and not area[0]:
						return redirect('login:choose_rsm')
					elif rsm[0] and area[0]:
					    if rsm[0] == 'indonesia timur':
					        request.session['rsm'] = 'timur'
					    else:
					        request.session['rsm'] = rsm[0]
					    request.session['area'] = '_'.join(area[0].split())
					    return redirect('dashboard:dashboard')
				
				else:
					form = Login()
					messages.error(request, 'Password Salah')
					

			else:
				form = Login()
				messages.error(request, 'Username Tidak Ditemukan')
				

		else:
			form = Login()
		return render(request, 'login.html', {'form':form})


	else:
		return redirect('dashboard:dashboard')

@csrf_exempt		
def choose_rsm(request):
	if 'logged_in' in request.session or not request.session['logged_in']:
		email = request.session['email']
		cursor = connection.cursor()
		
		cursor.execute("SELECT area FROM PROFILE WHERE email = '"+email+"';")
		area = cursor.fetchone()
		
		
		
		if request.method == 'POST' and request.POST['action'] == 'sumatera':
			cursor.execute("UPDATE profile set rsm = 'sumatera' where email = '"+email+"';")
			cursor.close()
			if area[0]:
			    request.session['rsm']='sumatera'
			    request.session['area']='_'.join(area[0].split())
			    return redirect('dashboard:dashboard')
			else:
			    return redirect('login:choose_area')
		elif request.method == 'POST' and request.POST['action'] == 'jawa':
			cursor.execute("UPDATE profile set rsm = 'jawa' where email = '"+email+"';")
			cursor.close()
			if area[0]:
			    request.session['rsm']='jawa'
			    request.session['area']='_'.join(area[0].split())
			    return redirect('dashboard:dashboard')
			else:
			    return redirect('login:choose_area')
		elif request.method == 'POST' and request.POST['action'] == 'indonesiaTimur':
			cursor.execute("UPDATE profile set rsm = 'indonesia timur' where email = '"+email+"';")
			cursor.close()
			if area[0]:
			    request.session['rsm']='timur'
			    request.session['area']='_'.join(area[0].split())
			    return redirect('dashboard:dashboard')
			else:
			    return redirect('login:choose_area')	
		else:
			return render(request,'verifikasi_rsm.html')
	else:
		return redirect('dashboard:dashboard')
		
@csrf_exempt		
def choose_area(request):
	cursor = connection.cursor()
	email = request.session['email']

	cursor.execute("SELECT rsm FROM PROFILE WHERE email = '"+email+"';")
	rsm = cursor.fetchone()
	if 'logged_in' in request.session or not request.session['logged_in']:
	    cursor.execute("SELECT area FROM PROFILE WHERE email = '"+email+"';")
	    area = cursor.fetchone()
	    if rsm[0] and area[0]:
	        return redirect('dashboard:dashboard')
	    elif rsm[0] and not area[0]:
	        if request.method == 'POST':
	            if rsm[0] == 'sumatera':
	                if request.POST['action'] == 'lampung_bengkulu':
	                    cursor.execute("UPDATE profile set area = 'lampung bengkulu' where email = '"+email+"';")
	                    request.session['area']='lampung_bengkulu'
	                elif request.POST['action'] == 'sumatera_selatan':
	                    cursor.execute("UPDATE profile set area = 'sumatera selatan' where email = '"+email+"';")
	                    request.session['area']='sumatera_selatan'
	                elif request.POST['action'] == 'sumatera_tengah':
	                    cursor.execute("UPDATE profile set area = 'sumatera tengah' where email = '"+email+"';")
	                    request.session['area']='sumatera_tengah'
	                elif request.POST['action'] == 'sumatera_utara':
	                    cursor.execute("UPDATE profile set area = 'sumatera utara' where email = '"+email+"';")
	                    request.session['area']='sumatera_utara'
	            
	            elif rsm[0] == 'jawa':
	                if request.POST['action'] == 'jawa_timur':
	                    cursor.execute("UPDATE profile set area = 'jawa timur' where email = '"+email+"';")
	                    request.session['area']='jawa_timur'
	                elif request.POST['action'] == 'jawa_tengah':
	                    cursor.execute("UPDATE profile set area = 'jawa tengah' where email = '"+email+"';")
	                    request.session['area']='jawa_tengah'
	                elif request.POST['action'] == 'jawa_barat':
	                    cursor.execute("UPDATE profile set area = 'jawa barat' where email = '"+email+"';")
	                    request.session['area']='jawa_barat'
	            
	            elif rsm[0] == 'indonesia timur':
	                if request.POST['action'] == 'sulawesi':
	                    cursor.execute("UPDATE profile set area = 'sulawesi' where email = '"+email+"';")
	                    request.session['area']='sulawesi'
	                elif request.POST['action'] == 'kalimantan':
	                    cursor.execute("UPDATE profile set area = 'kalimantan' where email = '"+email+"';")
	                    request.session['area']='kalimantan'
	            cursor.close()
	            return redirect('dashboard:dashboard')
	        else:
	            return render(request,'verifikasi_area.html', {'rsm':rsm[0]})
	    else:
	        return redirect('login:choose_rsm')
	
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
# 		print(user_data[0])
# 		if user_data[0] == "default" or user_data[1] == "default" or user_data[2] == "default":
# 		    user_data[0] = user.email
# 		    user_data[1] = user.username
# 		    if request.session["password1"]:
# 		        user_data[2] = request.session["password1"]
# 		    else:
# 		        user_data[2] = user.password
# 		cursor.execute("INSERT INTO pengguna (email, username, password) VALUES"
# 						"('"+user_data[0]+"', '"+user_data[1]+"', '"+user_data[2]+"');")
# 		cursor.execute("INSERT INTO profile (email, role) VALUES"
# 						"('"+user_data[0]+"', 'karyawan');")
# 		request.session["email"] = user_data[0]
# 		request.session["username"] = user_data[1]
# 		request.session["role"] = "karyawan"
# 		request.session["password1"] = user_data[2]
		request.session.modified = True
		cursor.execute("UPDATE pengguna set regis = 'ok' where email='"+user.email+"';")
		cursor.close()
		user.save()
		return redirect('login:verified')
	else:
		return redirect('login:failed_verified')

@csrf_exempt
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
		
def email_exist(request):
	if 'logged_in' not in request.session or not request.session['logged_in']:
		return render(request, 'email_already_exist.html')
	else:
		return redirect('dashboard:dashboard')    

def valid(request):
	if 'logged_in' not in request.session or not request.session['logged_in']:
		return render(request, 'valid.html')
	else:
		return redirect('dashboard:dashboard')    


def verification(request):
	if 'logged_in' not in request.session or not request.session['logged_in']:
		return render(request, 'verification.html')
	else:
		return redirect('dashboard:dashboard')

def verified(request):
	return render(request, 'response.html')

def failed_verified(request):
	return render(request, 'failed_verified.html')
	

