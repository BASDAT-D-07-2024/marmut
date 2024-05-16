from django.shortcuts import render, redirect
import uuid
import psycopg2
from datetime import date
from django.contrib import messages
from django.http import JsonResponse
from album.views import today_date
from utils.db_utils import get_db_connection
from django.views.decorators.cache import never_cache

@never_cache
def play_podcast(request):

    return render(request, "play_podcast.html")

def create_podcast(request):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    role = request.session.get('role')
    user = request.session.get('user')

    if 'podcaster' not in role:
        return redirect('main:dashboard')
    
    if request.method == 'POST':
        judul_podcast = request.POST.get('judul_podcast')
        genre = request.POST.getlist('genre')
        durasi = request.POST.get('durasi')

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            id_konten = uuid.uuid4()
            tanggal_rilis, tahun = today_date()
            cursor.execute('INSERT INTO KONTEN (id, judul, tanggal_rilis, tahun, durasi) VALUES (%s, %s, %s, %s, %s)', (id_konten, judul_podcast, tanggal_rilis, tahun, durasi))
            connection.commit()

            cursor.execute('INSERT INTO PODCAST (id_konten, email_podcaster) VALUES (%s, %s, %s, %s, %s)', (id_konten, user['email']))
            connection.commit()

            for i in range(len(genre)):
                cursor.execute('INSERT INTO GENRE (id_konten, genre) VALUES (%s, %s)', (id_konten, genre[i]))
                connection.commit()

            messages.success(request, 'Song created successfully')
            return redirect('podcast:list_podcast')
        except psycopg2.Error as error:
            messages.error(request, 'Error while inserting data to database')
            return redirect('podcast:create_podcast')
        finally:
            if connection:
                cursor.close()
                connection.close()

def create_ep_podcast(request):

    return render(request, "create_ep_podcast.html")

def list_podcast(request):

    return render(request, "list_podcast.html")

def list_ep_podcast(request):

    return render(request, "list_ep_podcast.html")