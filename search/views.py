import uuid
import psycopg2
from datetime import date
from django.contrib import messages
from django.http import JsonResponse
from utils.db_utils import get_db_connection
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def search_result(request):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    role = request.session.get('role')
    user = request.session.get('user')

    if 'label' not in role:
        if request.method == 'POST':
            search_text = "%" + request.POST.get('search_text') + "%"
            context = {
                'search_text': request.POST.get('search_text'),
                'songs': [],
                'podcasts': [],
                'playlists': [],
            }
            try:
                connection = get_db_connection()
                cursor = connection.cursor()

                cursor.execute('SELECT s.id_konten, k.judul, a.nama FROM SONG s JOIN ARTIST ar ON s.id_artist = ar.id JOIN AKUN a ON ar.email_akun = a.email JOIN KONTEN k ON s.id_konten = k.id WHERE k.judul ILIKE %s', (search_text,))
                songs = cursor.fetchall()
                print(songs)
                for song in songs:
                    context['songs'].append({
                        'id': song[0],
                        'judul': song[1],
                        'oleh': song[2],
                        'tipe': 'SONG',
                    })

                cursor.execute('SELECT pc.id_konten, k.judul, a.nama FROM PODCAST pc JOIN PODCASTER p ON pc.email_podcaster = p.email JOIN AKUN a ON p.email = a.email JOIN KONTEN k ON pc.id_konten = k.id WHERE k.judul ILIKE %s', (search_text,))
                podcasts = cursor.fetchall()
                for podcast in podcasts:
                    context['podcasts'].append({
                        'id': podcast[0],
                        'judul': podcast[1],
                        'oleh': podcast[2],
                        'tipe': 'PODCAST',
                    })
                
                cursor.execute('SELECT UP.id_playlist, UP.judul, A.nama FROM USER_PLAYLIST UP JOIN AKUN A ON UP.email_pembuat = A.email WHERE UP.judul ILIKE %s', (search_text,))
                playlists = cursor.fetchall()
                for playlist in playlists:
                    context['playlists'].append({
                        'id': playlist[0],
                        'judul': playlist[1],
                        'oleh': playlist[2],
                        'tipe': 'USER PLAYLIST',
                    })
            except psycopg2.Error as e:
                messages.error(request, 'Error fetching search result')
            finally:
                cursor.close()
                connection.close()

            return render(request, 'search-result.html', context)
    return redirect('main:dashboard')