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
            if is_label(email):
                cursor.execute("SELECT * FROM label WHERE email = %s AND password = %s", (email, password))
            else:
                cursor.execute("SELECT * FROM akun WHERE email = %s AND password = %s", (email, password))
            user = cursor.fetchone()

            if user is not None:
                request.session['role'] = []
                if is_label(email):
                    request.session['username'] = user[1]
                    request.session['role'] += ['label']
                else:
                    request.session['username'] = user[2]
                    if is_premium(email):
                        request.session['role'] += ['premium']
                    else:
                        request.session['role'] += ['nonpremium']
                    if is_podcaster(email):
                        request.session['role'] += ['podcaster']
                    if is_artist(email):
                        request.session['role'] += ['artist']
                    if is_songwriter(email):
                        request.session['role'] += ['songwriter']
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

def is_premium(email):
    try:
        connection = get_db_connection()

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM premium WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user is not None:
            return True
        else:
            return False

    except psycopg2.Error as e:
        print(e)
        return HttpResponse("Error occurred while connecting to the database")

    finally:
        if connection:
            cursor.close()
            connection.close()

def is_podcaster(email):
    try:
        connection = get_db_connection()

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM podcaster WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user is not None:
            return True
        else:
            return False

    except psycopg2.Error as e:
        print(e)
        return HttpResponse("Error occurred while connecting to the database")

    finally:
        if connection:
            cursor.close()
            connection.close()

def is_artist(email):
    try:
        connection = get_db_connection()

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM artist WHERE email_akun = %s", (email,))
        user = cursor.fetchone()

        if user is not None:
            return True
        else:
            return False

    except psycopg2.Error as e:
        print(e)
        return HttpResponse("Error occurred while connecting to the database")

    finally:
        if connection:
            cursor.close()
            connection.close()

def is_songwriter(email):
    try:
        connection = get_db_connection()

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM songwriter WHERE email_akun = %s", (email,))
        user = cursor.fetchone()

        if user is not None:
            return True
        else:
            return False

    except psycopg2.Error as e:
        print(e)
        return HttpResponse("Error occurred while connecting to the database")

    finally:
        if connection:
            cursor.close()
            connection.close()

def is_label(email):
    try:
        connection = get_db_connection()

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM label WHERE email = %s", (email,))
        label = cursor.fetchone()

        if label is not None:
            return True
        else:
            return False

    except psycopg2.Error as e:
        print(e)
        return HttpResponse("Error occurred while connecting to the database")

    finally:
        if connection:
            cursor.close()
            connection.close()