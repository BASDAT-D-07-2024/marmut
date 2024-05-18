import psycopg2
from utils.db_utils import get_db_connection
from django.shortcuts import render, redirect

def dashboard(request):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    role = request.session.get('role')
    user = request.session.get('user')

    context = {}
    context.update(user)

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM USER_PLAYLIST WHERE email_pembuat = %s', (user['email'],))
        playlists = cursor.fetchall()
        context['playlists'] = []
        for playlist in playlists:
            playlist = {
                'id': playlist[1],
                'judul': playlist[2],
                'jumlah_lagu': playlist[4],
                'total_durasi': playlist[7],
            }
            context['playlists'].append(playlist)
        
        if 'label' in role:
            context['albums'] = []
            cursor.execute('SELECT id FROM LABEL WHERE email = %s', (user['email'],))
            label_id = cursor.fetchone()[0]

            cursor.execute('SELECT * FROM ALBUM WHERE id_label = %s', (label_id,))
            albums = cursor.fetchall()

            for i in range(len(albums)):
                album = {
                    'id': albums[i][0],
                    'judul': albums[i][1],
                    'jumlah_lagu': albums[i][2],
                    'total_durasi': albums[i][4],
                }
                context['albums'].append(album)
            return render(request, 'dashboard-label.html', context)
        else:
            roles_capitalized = [role.capitalize() for role in role]
            roles_string = ', '.join(roles_capitalized)
    
            context['is_podcaster'] = 'podcaster' in role
            context['is_artist'] = 'artist' in role
            context['is_songwriter'] = 'songwriter' in role
            context['roles'] = roles_string

            if 'podcaster' in role:
                cursor.execute('SELECT * FROM PODCAST WHERE email_podcaster = %s', (user['email'],))
                podcasts = cursor.fetchall()
                context['podcasts'] = []
                for podcast in podcasts:
                    cursor.execute('SELECT judul, durasi FROM KONTEN WHERE id = %s', (podcast[0],))
                    judul, durasi = cursor.fetchone()
                    cursor.execute('SELECT * FROM EPISODE WHERE id_konten_podcast = %s', (podcast[0],))
                    episodes = cursor.fetchall()
                    podcast = {
                        'id': podcast[0],
                        'judul': judul,
                        'jumlah_episode': len(episodes),
                        'total_durasi': durasi,
                    }
                    context['podcasts'].append(podcast)

            if 'artist' in role:
                cursor.execute('SELECT * FROM ARTIST WHERE email_akun = %s', (user['email'],))
                artist = cursor.fetchone()
                cursor.execute('SELECT * FROM SONG WHERE id_artist = %s', (artist[0],))
                songs = cursor.fetchall()
                context['songs'] = []
                for i in range(len(songs)):
                    cursor.execute('SELECT judul, durasi FROM KONTEN WHERE id = %s', (songs[i][0],))
                    judul, durasi = cursor.fetchone()
                    song = {
                        'id': songs[i][0],
                        'judul': judul,
                        'durasi': durasi,
                        'total_play': songs[i][3],
                        'total_download': songs[i][4],
                    }
                    context['songs'].append(song)

            if 'songwriter' in role:
                cursor.execute('SELECT * FROM SONGWRITER WHERE email_akun = %s', (user['email'],))
                songwriter = cursor.fetchone()
                cursor.execute('SELECT * FROM SONGWRITER_WRITE_SONG WHERE id_songwriter = %s', (songwriter[0],))
                songs = cursor.fetchall()
                context['songs'] = []
                for i in range(len(songs)):
                    cursor.execute('SELECT judul, durasi FROM KONTEN WHERE id = %s', (songs[i][1],))
                    judul, durasi = cursor.fetchone()
                    cursor.execute('SELECT total_play, total_download FROM SONG WHERE id_konten = %s', (songs[i][1],))
                    total_play, total_download = cursor.fetchone()
                    song = {
                        'id': songs[i][0],
                        'judul': judul,
                        'durasi': durasi,
                        'total_play': total_play,
                        'total_download': total_download,
                    }
                    context['songs'].append(song)
    except psycopg2.Error as e:
        print(e)
    finally:
        if connection:
            cursor.close()
            connection.close()
    return render(request, 'dashboard.html', context)
