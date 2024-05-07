import psycopg2
from utils.db_utils import get_db_connection
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods

@require_http_methods(['GET'])
def login_register(request):
    if request.session.get('username') is not None:
        return redirect('dashboard')
    return render(request, 'login-register.html')

@require_http_methods(['GET', 'POST'])
def login(request):
    if request.session.get('username') is not None:
        return redirect('dashboard')
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            connection = get_db_connection()

            cursor = connection.cursor()
            cursor.execute("SELECT * FROM akun WHERE email = %s AND password = %s", (email, password))
            user = cursor.fetchone()

            if user is not None:
                request.session['username'] = user[2]
                return redirect('main:dashboard')
            else:
                messages.error(request, 'Email or password is incorrect')
                return redirect('authentication:login')

        except psycopg2.Error as e:
            print(e)
            return HttpResponse("Error occurred while connecting to the database")

        finally:
            if connection:
                cursor.close()
                connection.close()

    else:
        return render(request, 'login.html')

@require_http_methods(['GET'])
def register(request):
    if request.session.get('username') is not None:
        return redirect('dashboard')
    return render(request, 'register.html')

@require_http_methods(['GET', 'POST'])
def register_user(request):
    if request.session.get('username') is not None:
        return redirect('dashboard')
    return render(request, 'register-user.html')

@require_http_methods(['GET', 'POST'])
def register_label(request):
    if request.session.get('username') is not None:
        return redirect('dashboard')
    return render(request, 'register-label.html')

@require_http_methods(['GET'])
def logout(request):
    request.session.flush()
    return redirect('authentication:login_register')