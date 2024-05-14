import psycopg2
from django.contrib import messages
from utils.db_utils import get_db_connection
from django.shortcuts import render, redirect

def list_album(request):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    role = request.session.get('role')
    user = request.session.get('user')

    context = {
        'albums': [],
        'is_label': 'label' in role,
        'is_artist': 'artist' in role,
        'is_songwriter': 'songwriter' in role,
    }

    if 'label' in role or 'artist' in role or 'songwriter' in role:
        try:
            connection = get_db_connection()      
            cursor = connection.cursor()
            if 'label' in role:
                cursor.execute('SELECT * FROM LABEL WHERE email = %s', (user['email'],))
                label = cursor.fetchone()

                cursor.execute('SELECT * FROM ALBUM WHERE id_label = %s', (label[0],))
                albums = cursor.fetchall()

                for i in range(len(albums)):
                    album = {
                        'id': albums[i][0],
                        'judul': albums[i][1],
                        'jumlah_lagu': albums[i][2],
                        'total_durasi': albums[i][4],
                    }
                    context['albums'].append(album)

                return render(request, 'list-album.html', context)
            elif 'artist' in role or 'songwriter' in role:
                cursor.execute('SELECT * FROM ALBUM')
                albums = cursor.fetchall()

                for i in range(len(albums)):
                    cursor.execute('SELECT nama FROM LABEL WHERE id = %s', (albums[i][3],))
                    label = cursor.fetchone()
                    album = {
                        'id': albums[i][0],
                        'judul': albums[i][1],
                        'label': label[0],
                        'jumlah_lagu': albums[i][2],
                        'total_durasi': albums[i][4],
                    }
                    context['albums'].append(album)

                return render(request, 'list-album.html', context)
        except psycopg2.Error as error:
            messages.error(request, 'Error while fetching data from database')
            return render(request, 'list-album.html')
        finally:
            if connection:
                cursor.close()
                connection.close()
    return redirect('main:dashboard')

def view_album(request, id):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    role = request.session.get('role')

    context = {
        'id': id,
        'songs': [],
    }

    if 'label' in role or 'artist' in role or 'songwriter' in role:
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute('SELECT * FROM ALBUM WHERE id = %s', (id,))
            album = cursor.fetchone()
            context['judul'] = album[1]

            cursor.execute('SELECT * FROM SONG WHERE id_album = %s', (id,))
            songs = cursor.fetchall()

            for i in range(len(songs)):
                cursor.execute('SELECT judul, durasi FROM KONTEN WHERE id = %s', (songs[i][0],))
                konten = cursor.fetchone()

                cursor.execute('SELECT count(*) FROM DOWNLOADED_SONG WHERE id_song = %s', (songs[i][0],))
                total_download = cursor.fetchone()

                song = {
                    'id': songs[i][0],
                    'judul': konten[0],
                    'durasi': konten[1],
                    'total_play': songs[i][3],
                    'total_download': total_download[0],
                }
                context['songs'].append(song)

            return render(request, 'view-album.html', context)
        except psycopg2.Error as error:
            messages.error(request, 'Error while fetching data from database')
            return render(request, 'view-album.html')
        finally:
            if connection:
                cursor.close()
                connection.close()
    return redirect('main:dashboard')
