import uuid
import psycopg2
from datetime import date
from django.contrib import messages
from django.http import JsonResponse
from utils.db_utils import get_db_connection
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache

# Create your views here.
def list_download(request):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    role = request.session.get('role')
    user = request.session.get('user')
    email_downloader = user['email']
    context = {
        'downloaded_songs': [],
    }
    if 'premium' in role:
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute('SELECT ds.id_song, k.judul AS judul_lagu, a.nama AS nama_artist FROM DOWNLOADED_SONG ds JOIN SONG s ON ds.id_song = s.id_konten JOIN KONTEN k ON s.id_konten = k.id JOIN ARTIST ar ON s.id_artist = ar.id JOIN AKUN a ON ar.email_akun = a.email WHERE ds.email_downloader = %s', (email_downloader,))
            downloaded_songs = cursor.fetchall()
            for song in downloaded_songs:
                context['downloaded_songs'].append({
                    'id': song[0],
                    'title': song[1],
                    'artist': song[2]
                })
        except psycopg2.Error as e:
            messages.error(request, 'Error fetching downloads')
        finally:
            cursor.close()
            connection.close()

    return render(request, 'list-download.html', context)

def delete_download(request, id_song):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    role = request.session.get('role')
    user = request.session.get('user')
    email_downloader = user['email']

    if request.method == 'POST':
        if 'premium' in role:
            try:
                connection = get_db_connection()
                cursor = connection.cursor()

                cursor.execute('DELETE FROM DOWNLOADED_SONG WHERE id_song = %s AND email_downloader = %s', (id_song, email_downloader))
                connection.commit()
                messages.success(request, 'Song deleted successfully')
            except psycopg2.Error as e:
                messages.error(request, 'Error deleting song')
            finally:
                cursor.close()
                connection.close()

    return redirect('download:list_download')