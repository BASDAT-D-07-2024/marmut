from django.shortcuts import render, redirect
import uuid
import psycopg2
from datetime import date
from django.contrib import messages
from django.http import JsonResponse
from utils.db_utils import get_db_connection
from django.views.decorators.cache import never_cache

@never_cache
def chart_list(request):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    role = request.session.get('role')

    context = {
        'charts': [],
        'is_label': 'label' in role,
        'is_artist': 'artist' in role,
        'is_songwriter': 'songwriter' in role,
    }

    if 'label' not in role:
        try:
            connection = get_db_connection()      
            cursor = connection.cursor()
            
            cursor.execute('SELECT * FROM CHART')
            charts = cursor.fetchall()

            for i in range(len(charts)):
                chart = {
                    'tipe': charts[i][0],
                    'id_playlist': charts[i][1],
                }
                context['charts'].append(chart)

            return render(request, 'chart_list.html', context)
        except psycopg2.Error as error:
            messages.error(request, 'Error while fetching data from database')
            return render(request, 'chart_list.html')
        finally:
            if connection:
                cursor.close()
                connection.close()
    
    return redirect('main:dashboard')

def chart_detail(request, id):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    role = request.session.get('role')

    context = {
        'id': id,
        'songs_id': [],
    }

    if 'label' not in role:
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Fetch the chart details
            cursor.execute('SELECT * FROM CHART WHERE id_playlist = %s', (id,))
            chart = cursor.fetchone()
            if chart:
                context['nama'] = chart[0]

                # Fetch the top 20 songs based on the chart type
                if context['nama'] == 'Daily Top 20':
                    cursor.execute("SELECT * FROM SONG s JOIN KONTEN k ON s.id_konten = k.id WHERE k.tanggal_rilis >= CURRENT_DATE - INTERVAL '1 day' AND s.total_play > 0 ORDER BY s.total_play DESC LIMIT 20")
                    top_20 = cursor.fetchall()
                elif context['nama'] == 'Weekly Top 20':
                    cursor.execute("SELECT * FROM SONG s JOIN KONTEN k ON s.id_konten = k.id WHERE k.tanggal_rilis >= CURRENT_DATE - INTERVAL '1 week' AND s.total_play > 0 ORDER BY s.total_play DESC LIMIT 20")
                    top_20 = cursor.fetchall()
                elif context['nama'] == 'Monthly Top 20':
                    cursor.execute("SELECT * FROM SONG s JOIN KONTEN k ON s.id_konten = k.id WHERE k.tanggal_rilis >= CURRENT_DATE - INTERVAL '1 month' AND s.total_play > 0 ORDER BY s.total_play DESC LIMIT 20")
                    top_20 = cursor.fetchall()
                elif context['nama'] == 'Yearly Top 20':
                    cursor.execute("SELECT * FROM SONG s JOIN KONTEN k ON s.id_konten = k.id WHERE k.tanggal_rilis >= CURRENT_DATE - INTERVAL '1 year' AND s.total_play > 0 ORDER BY s.total_play DESC LIMIT 20")
                    top_20 = cursor.fetchall()
                
                # Update the playlist songs
                cursor.execute('DELETE FROM PLAYLIST_SONG WHERE id_playlist = %s', (id,))
                connection.commit()

                for songs in top_20:
                    cursor.execute('INSERT INTO PLAYLIST_SONG (id_playlist, id_song) VALUES (%s, %s)', (id, songs[0]))
                    connection.commit()

                # Fetch the songs in the playlist
                cursor.execute('SELECT * FROM PLAYLIST_SONG WHERE id_playlist = %s', (id,))
                songs_id = cursor.fetchall()

                for song_id in songs_id:
                    cursor.execute('''
                        SELECT 
                            KONTEN.judul, 
                            KONTEN.tanggal_rilis, 
                            SONG.total_play, 
                            AKUN.nama AS artis
                        FROM 
                            KONTEN
                        JOIN 
                            SONG ON KONTEN.id = SONG.id_konten
                        JOIN 
                            ARTIST ON SONG.id_artist = ARTIST.id
                        JOIN 
                            AKUN ON ARTIST.email_akun = AKUN.email
                        WHERE 
                            KONTEN.id = %s
                    ''', (song_id[1],))
                    konten = cursor.fetchone()

                    if konten:
                        song = {
                            'judul': konten[0],
                            'tanggal_rilis': konten[1],
                            'total_play': konten[2],
                            'artis': konten[3],
                        }
                        context['songs_id'].append(song)

            return render(request, 'chart_detail.html', context)
        except psycopg2.Error as error:
            messages.error(request, 'Error while fetching data from database')
            return render(request, 'chart_detail.html', context)
        finally:
            if connection:
                cursor.close()
                connection.close()
    return redirect('main:dashboard')