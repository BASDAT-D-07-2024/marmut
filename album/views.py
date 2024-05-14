import uuid
from django.http import JsonResponse
import psycopg2
from datetime import date
from django.contrib import messages
from utils.db_utils import get_db_connection
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

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

def create_album(request):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    role = request.session.get('role')
    user = request.session.get('user')

    if request.method == 'POST':
        judul_album = request.POST.get('judul_album')
        id_label = request.POST.get('label')
        judul_lagu = request.POST.get('judul_lagu')
        if 'artist' in role:
            id_artist = request.POST.get('artist_id')
        else:
            id_artist = request.POST.getlist('artist')
        id_songwriter = request.POST.getlist('songwriter')
        genre = request.POST.getlist('genre')
        durasi = request.POST.get('durasi')

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            id_album = uuid.uuid4()
            cursor.execute('INSERT INTO ALBUM (id, judul, jumlah_lagu, id_label, total_durasi) VALUES (%s, %s, %s, %s, %s)', (id_album, judul_album, 1, id_label, durasi))
            connection.commit()

            id_konten = uuid.uuid4()
            tanggal_rilis, tahun = today_date()
            cursor.execute('INSERT INTO KONTEN (id, judul, tanggal_rilis, tahun, durasi) VALUES (%s, %s, %s, %s, %s)', (id_konten, judul_lagu, tanggal_rilis, tahun, durasi))
            connection.commit()

            cursor.execute('INSERT INTO SONG (id_konten, id_artist, id_album, total_play, total_download) VALUES (%s, %s, %s, %s, %s)', (id_konten, id_artist, id_album, 0, 0))
            connection.commit()

            for i in range(len(genre)):
                cursor.execute('INSERT INTO GENRE (id_konten, genre) VALUES (%s, %s)', (id_konten, genre[i]))
                connection.commit()

            for i in range(len(id_songwriter)):
                cursor.execute('INSERT INTO SONGWRITER_WRITE_SONG (id_songwriter, id_song) VALUES (%s, %s)', (id_songwriter[i], id_konten))
                connection.commit()

            messages.success(request, 'Album created successfully')
            return redirect('album:list_album')
        except psycopg2.Error as error:
            messages.error(request, 'Error while inserting data to database')
            return redirect('album:create_album')
        finally:
            if connection:
                cursor.close()
                connection.close()

    context = {
        'is_artist': 'artist' in role,
        'is_songwriter': 'songwriter' in role,
        'labels': [],
        'artists': [],
        'songwriters': [],
        'genres': [],
    }

    if 'artist' in role or 'songwriter' in role:
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Get all labels
            cursor.execute('SELECT * FROM LABEL')
            labels = cursor.fetchall()

            for i in range(len(labels)):
                label = {
                    'id': labels[i][0],
                    'nama': labels[i][1],
                }
                context['labels'].append(label)
            
            # Get all artists
            cursor.execute('SELECT * FROM SONGWRITER')
            songwriter = cursor.fetchall()
            
            for i in range(len(songwriter)):
                cursor.execute('SELECT nama FROM AKUN WHERE email = %s', (songwriter[i][1],))
                nama = cursor.fetchone()
                songwrite = {
                    'id': songwriter[i][0],
                    'nama': nama[0],
                }
                context['songwriters'].append(songwrite)
            
            # Get all songwriters
            cursor.execute('SELECT * FROM ARTIST')
            artist = cursor.fetchall()
            
            for i in range(len(artist)):
                cursor.execute('SELECT nama FROM AKUN WHERE email = %s', (artist[i][1],))
                nama = cursor.fetchone()
                artis = {
                    'id': artist[i][0],
                    'nama': nama[0],
                }
                context['artists'].append(artis)

            # Auto choose artist if the user is an artist
            if 'artist' in role:
                cursor.execute('SELECT * FROM ARTIST WHERE email_akun = %s', (user['email'],))
                artist = cursor.fetchone()
                context['artist'] = {
                    'id': artist[0],
                    'nama': user['nama'],
                }

            # Auto choose songwriter if the user is a songwriter
            if 'songwriter' in role:
                cursor.execute('SELECT * FROM SONGWRITER WHERE email_akun = %s', (user['email'],))
                songwriter = cursor.fetchone()
                context['songwriter'] = {
                    'id': songwriter[0],
                    'nama': user['nama'],
                }
            
            # Get all genres
            cursor.execute('SELECT DISTINCT on (genre) * FROM GENRE')
            genres = cursor.fetchall()
            for i in range(len(genres)):
                genre = {
                    'id': genres[i][0],
                    'genre': genres[i][1],
                }
                context['genres'].append(genre)

            return render(request, 'create-album.html', context)
        except psycopg2.Error as error:
            messages.error(request, 'Error while fetching data from database')
            return render(request, 'create-album.html')
        finally:
            if connection:
                cursor.close()
                connection.close()
    return redirect('main:dashboard')

@require_http_methods(["DELETE"])
def delete_album(request, album_id):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    role = request.session.get('role')

    if 'label' in role or 'artist' in role or 'songwriter' in role:
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute('SELECT * FROM ALBUM WHERE id = %s', (album_id,))
            album = cursor.fetchone()

            if album is None:
                return JsonResponse({'message': 'Album not found'}, status=404)
            
            cursor.execute('SELECT * FROM SONG WHERE id_album = %s', (album_id,))
            songs = cursor.fetchall()

            for i in range(len(songs)):
                cursor.execute('DELETE FROM KONTEN WHERE id = %s', (songs[i][0],))
                connection.commit()

            cursor.execute('DELETE FROM ALBUM WHERE id = %s', (album_id,))
            connection.commit()
            return JsonResponse({'message': 'Album deleted successfully'}, status=200)
        except psycopg2.Error as error:
            return JsonResponse({'message': 'Error while deleting album'}, status=500)
        finally:
            if connection:
                cursor.close()
                connection.close()

def today_date():
    today = date.today()
    return (today.strftime('%Y-%m-%d'), today.strftime('%Y'))