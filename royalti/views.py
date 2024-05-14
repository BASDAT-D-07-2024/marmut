import psycopg2
from django.contrib import messages
from utils.db_utils import get_db_connection
from django.shortcuts import render, redirect

def royalti(request):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    role = request.session.get('role')
    user = request.session.get('user')

    if 'label' in role or 'artist' in role or 'songwriter' in role:
        try:
            connection = get_db_connection()      
            cursor = connection.cursor()

            context = {
                'royalties': [],
            }

            if 'label' in role:
                cursor.execute('SELECT * FROM LABEL WHERE email = %s', (user['email'],))
                user = cursor.fetchone()

                cursor.execute('SELECT * FROM PEMILIK_HAK_CIPTA WHERE id = %s', (user[5],))
                pemilik_hak_cipta = cursor.fetchone()
                rate_royalti = pemilik_hak_cipta[1]

                cursor.execute('SELECT * FROM ALBUM WHERE id_label = %s', (user[0],))
                albums = cursor.fetchall()

                for i in range(len(albums)):
                    cursor.execute('SELECT * FROM SONG WHERE id_album = %s', (albums[i][0],))
                    songs = cursor.fetchall()

                    for j in range(len(songs)):
                        cursor.execute('SELECT judul FROM KONTEN WHERE id = %s', (songs[j][0],))
                        judul_lagu = cursor.fetchone()
                        
                        royalti = {
                            'judul_lagu': judul_lagu[0],
                            'judul_album': albums[i][1],
                            'total_play': songs[j][3],
                            'total_download': songs[j][4],
                            'total_royalti': songs[j][3] * rate_royalti,
                        }

                        context['royalties'].append(royalti)
            elif 'artist' in role or 'songwriter' in role:
                if 'artist' in role:
                    cursor.execute('SELECT * FROM ARTIST WHERE email_akun = %s', (user['email'],))
                    user = cursor.fetchone()
                elif 'songwriter' in role:
                    cursor.execute('SELECT * FROM SONGWRITER WHERE email_akun = %s', (user['email'],))
                    user = cursor.fetchone()

                cursor.execute('SELECT * FROM PEMILIK_HAK_CIPTA WHERE id = %s', (user[2],))
                pemilik_hak_cipta = cursor.fetchone()
                rate_royalti = pemilik_hak_cipta[1]

                cursor.execute('SELECT * FROM SONG WHERE id_artist = %s', (user[0],))
                songs = cursor.fetchall()

                for i in range(len(songs)):
                    cursor.execute('SELECT judul FROM KONTEN WHERE id = %s', (songs[i][0],))
                    judul_lagu = cursor.fetchone()

                    cursor.execute('SELECT judul FROM ALBUM WHERE id = %s', (songs[i][2],))
                    judul_album = cursor.fetchone()
                    
                    royalti = {
                        'judul_lagu': judul_lagu[0],
                        'judul_album': judul_album[0],
                        'total_play': songs[i][3],
                        'total_download': songs[i][4],
                        'total_royalti': songs[i][3] * rate_royalti,
                    }

                    context['royalties'].append(royalti)

            return render(request, 'list-royalti.html', context)
        except psycopg2.Error as e:
            print(e)
            return redirect('main:dashboard')
        finally:
            if connection:
                cursor.close()
                connection.close()
    return redirect('main:dashboard')