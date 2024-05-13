import locale
import psycopg2
import uuid
from utils.db_utils import get_db_connection
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

@require_http_methods(['GET'])
def login_register(request):
    if request.session.get('role') is not None:
        return redirect('main:dashboard')
    return render(request, 'login-register.html')

@require_http_methods(['GET', 'POST'])
def login(request):
    if request.session.get('role') is not None:
        return redirect('main:dashboard')
    
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
                    request.session['user'] = extract_label_data(user)
                    request.session['role'] += ['label']
                else:
                    request.session['user'] = extract_user_data(user)
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
                messages.error(request, 'Email or password is incorrect!')
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
    if request.session.get('role') is not None:
        return redirect('main:dashboard')
    return render(request, 'register.html')

@require_http_methods(['GET', 'POST'])
def register_user(request):
    if request.session.get('role') is not None:
        return redirect('main:dashboard')
    return render(request, 'register-user.html')

@require_http_methods(['GET', 'POST'])
def register_label(request):
    if request.session.get('role') is not None:
        return redirect('main:dashboard')
    
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        nama = request.POST['name']
        kontak = request.POST['kontak']
        
        try:
            connection = get_db_connection()

            random_uuid_phc = uuid.uuid4()
            cursor = connection.cursor()
            cursor.execute("INSERT INTO PEMILIK_HAK_CIPTA (id, rate_royalti) VALUES (%s, %s)", (random_uuid_phc, 10000))
            connection.commit()

            random_uuid_label = uuid.uuid4()
            cursor = connection.cursor()
            cursor.execute("INSERT INTO label (id, nama, email, password, kontak, id_pemilik_hak_cipta) VALUES (%s, %s, %s, %s, %s, %s)", (random_uuid_label, nama, email, password, kontak, random_uuid_phc))
            connection.commit()
            messages.success(request, 'Registration successful!')

            return redirect('authentication:login')

        except psycopg2.Error as e:
            print(e)
            messages.error(request, 'Registration failed')
            return redirect('authentication:register_label')

        finally:
            if connection:
                cursor.close()
                connection.close()
    return render(request, 'register-label.html')

@require_http_methods(['GET'])
def logout(request):
    request.session.flush()
    return redirect('authentication:login_register')

def extract_user_data(user):
    gender = 'Laki-laki' if user[3] == 1 else 'Perempuan'
    x = user[5]
    locale.setlocale(locale.LC_ALL, 'id_ID')
    tanggal_lahir = f'{x.strftime("%d")} {x.strftime("%B")} {x.strftime("%Y")}'
    return {
        'email': user[0],
        'nama': user[2],
        'gender': gender,
        'tempat_lahir': user[4],
        'tanggal_lahir': tanggal_lahir,
        'is_verified': user[6],
        'kota_asal': user[7],
    }

def extract_label_data(label):
    return {
        'nama': label[1],
        'email': label[2],
        'kontak': label[4],
    }

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