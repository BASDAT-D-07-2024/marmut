from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.contrib import messages
from playlist.views import *
from authentication.views import is_premium
from utils.db_utils import get_db_connection
import uuid
from datetime import datetime
from psycopg2 import IntegrityError, DatabaseError
from psycopg2.errors import UniqueViolation

def show_playlist(request):
    connection = get_db_connection()
    if request.session.get('role') is None:
        return redirect('authentication:login')

    user = request.session.get('user')
    email = user['email']

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT up.judul, up.jumlah_lagu, up.total_durasi, up.id_user_playlist, up.id_playlist
            FROM USER_PLAYLIST up
            JOIN AKUN a ON up.email_pembuat = a.email
            JOIN PLAYLIST p ON up.id_playlist = p.id
            WHERE a.email = %s
        """, [email])

        hasil = cursor.fetchall()
        context = {
            "playlist": [{
                "judul": item[0],
                "jumlah_lagu": item[1],
                "total_durasi": item[2],
                "id_user_playlist": str(item[3]),
                "id_playlist": str(item[4])
            } for item in hasil]
        }

    return render(request, "show_playlist.html", context)

def user_playlist(request, playlist_id):
    
    if request.session.get('role') is None:
        return redirect('authentication:login')

    email = request.session.get('user', {}).get('email')
    if not email:
        return redirect('authentication:login')  # Redirect jika tidak ada email di session

    songs = []

    connection = get_db_connection()
    cursor = connection.cursor()
    # Execute your provided query
    cursor.execute("""
    SELECT 
        k.id AS song_id, 
        k.judul AS judul_lagu, 
        a_n.nama AS nama_artis, 
        up.judul AS judul_playlist, 
        up.jumlah_lagu, 
        up.deskripsi, 
        up.tanggal_dibuat, 
        p_n.nama AS nama_pembuat_playlist, 
        up.total_durasi,
        k.durasi,
        up.email_pembuat,
        up.id_user_playlist,
        up.total_durasi
    FROM user_playlist up
    JOIN akun p_n ON up.email_pembuat = p_n.email
    LEFT JOIN playlist_song ps ON up.id_playlist = ps.id_playlist
    LEFT JOIN konten k ON ps.id_song = k.id
    LEFT JOIN song s ON k.id = s.id_konten
    LEFT JOIN artist a ON s.id_artist = a.id
    LEFT JOIN akun a_n ON a.email_akun = a_n.email
    WHERE up.email_pembuat = %s AND up.id_playlist = %s;
    """, [email, playlist_id])
    
    hasil = cursor.fetchall()
    context = {}

    if hasil[0][10] == email:
        context["is_creator"] = True
    else:
        context["is_creator"] = False

    # Check if 'hasil' has any content
    if hasil:
        first_item = hasil[0]
        # Directly integrate playlist details into context
        context["judul_playlist"] = first_item[3]
        context["playlist_id"] = playlist_id
        context["deskripsi"] = first_item[5]
        context["jumlah_lagu"] = first_item[4]
        context["tanggal_dibuat"] = first_item[6]  # ensure date is formatted as string
        context["nama_pembuat"] = first_item[7]
        context["total_durasi"] = first_item[8]
        context["id_user_playlist"] = first_item[11]
        context["total_durasi"] = first_item[12]
        context["songs"] = False

        if (hasil[0][0] != None):
            context["songs"] = []
            for item in hasil:
                song_info = {
                    "id": str(item[0]),  # Ensure the ID is converted to string
                    "judul": item[1],
                    "nama_artis": item[2],
                    "durasi": item[9]
                }
                context["songs"].append(song_info)
    
    print(context)

    return render(request, "user_playlist.html", context)

def delete_song(request, playlist_id, song_id):
    email = request.session.get('user', {}).get('email')
    if not email:
        return redirect('authentication:login')

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            DELETE FROM PLAYLIST_SONG 
            WHERE id_SONG = %s AND ID_PLAYLIST = %s;
            """, [song_id, playlist_id])
        connection.commit()
        messages.success(request, "Song deleted successfully.")
    except IntegrityError as e:
        print(e)
        messages.error(request, "Integrity error: Unable to delete song. It may be linked to other records.")
    except DatabaseError as e:
        print(e)
        messages.error(request, "Database error: Unable to delete song.")
    except Exception as e:
        print(e)
        messages.error(request, "An unexpected error occurred.")
    finally:
        if connection:
            cursor.close()
            connection.close()
    
    return redirect('playlist:user_playlist', playlist_id=playlist_id)

def view_song(request, playlist_id, song_id):
    connection = get_db_connection()
    email = request.session.get('user', {}).get('email')
    if not email:
        return redirect('authentication:login')

    cursor = connection.cursor()
    cursor.execute(f"""
        SELECT 
            k.judul, 
            s.id_konten, 
            STRING_AGG(DISTINCT g.genre, ', ') AS genres,  -- Aggregate genres into a comma-separated string
            STRING_AGG(DISTINCT n.nama, ', ') AS songwriters,  -- Aggregate songwriters into a comma-separated string
            k.durasi, 
            k.tanggal_rilis, 
            s.total_play, 
            s.total_download, 
            al.judul AS album_judul, 
            k.tahun,
            a_ar.nama
        FROM song s
        JOIN playlist_song ps ON s.id_konten = ps.id_song
        JOIN konten k ON s.id_konten = k.id
        JOIN user_playlist up ON up.id_playlist = ps.id_playlist  -- Fetch user_playlist
        JOIN songwriter_write_song sws ON sws.id_song = s.id_konten  -- Fetch songwriters
        JOIN songwriter sw ON sws.id_songwriter = sw.id
        JOIN akun n ON sw.email_akun = n.email
        JOIN artist ar ON ar.id = s.id_artist
        JOIN akun a_ar ON ar.email_akun = a_ar.email
        JOIN genre g ON s.id_konten = g.id_konten  -- Fetch genres
        JOIN album al ON s.id_album = al.id  -- Fetch album name
        WHERE up.id_playlist = '{playlist_id}' 
        AND s.id_konten = '{song_id}'
        GROUP BY 
            k.judul, 
            s.id_konten, 
            k.durasi, 
            k.tanggal_rilis, 
            s.total_play, 
            s.total_download, 
            al.judul, 
            k.tahun,
            a_ar.nama;
    """)
    rows = cursor.fetchall()[0]

    song = {
        'judul': rows[0],
        'id': str(rows[1]),
        'genre': rows[2],
        'artist': rows[10],
        'durasi': rows[4],
        'tanggal_rilis': rows[5],
        'total_play':rows[6],
        'total_download':rows[7],
        'judul_album': rows[8],
        'tahun': rows[9],
        'is_premium': is_premium(email),
        'songwriter': rows[3],
    }

    return render(request, 'view_song.html', song)


def add_song(request, playlist_id):
    connection = get_db_connection()

    if request.method == 'POST':
        selected_song_id = request.POST.get('song')
        cursor = connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO playlist_song (id_playlist, id_song)
                VALUES (%s, %s);
                """, (str(playlist_id), selected_song_id))
            connection.commit()
            messages.success(request, "Song added successfully to the playlist.")
        except UniqueViolation as e:
            print(e)
            connection.rollback()  # Rollback the transaction on error
            messages.error(request, "This song is already in the playlist.")
        except Exception as e:
            print(e)
            connection.rollback()  # Rollback the transaction on error
            messages.error(request, "An unexpected error occurred.")
        finally:
            cursor.close()
            connection.close()

        return redirect('playlist:user_playlist', playlist_id=playlist_id)

    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT k.id, k.judul, ak.nama
            FROM song s
            JOIN konten k ON k.id = s.id_konten
            JOIN artist ar ON s.id_artist = ar.id
            JOIN akun ak ON ar.email_akun = ak.email;
        """)
        results = cursor.fetchall()
    finally:
        cursor.close()

    context = {
        'id_playlist': str(playlist_id),
        'songs': [{'id': str(row[0]), 'title': row[1], 'artist': row[2]}
                  for row in results]
    }
    return render(request, 'add_song.html', context)

def create_playlist(request):
    connection = get_db_connection()
    cursor = connection.cursor()
    email = request.session.get('user', {}).get('email')
    if not email:
        return redirect('authentication:login')
    
    if request.method == 'POST':
        judul = request.POST.get('judul')
        deskripsi = request.POST.get('deskripsi')
        print(judul, deskripsi)

        id_playlist = str(uuid.uuid4())
        current_datetime = datetime.now()
        formatted_date = current_datetime.strftime('%Y-%m-%d')
        cursor.execute(f"""
            INSERT INTO PLAYLIST (id)
            VALUES ('{id_playlist}');
        """)
        connection.commit()

        id_user_playlist = str(uuid.uuid4())
        cursor.execute(f"""
            INSERT INTO USER_PLAYLIST (EMAIL_PEMBUAT, ID_USER_PLAYLIST, judul, deskripsi, jumlah_lagu, tanggal_dibuat, id_playlist, total_durasi)
            VALUES ('{email}', '{id_user_playlist}', '{judul}', '{deskripsi}', 0, '{formatted_date}', '{id_playlist}', 0);
        """)
        connection.commit()

        return redirect('playlist:show_playlist')
    
    return render(request, 'create_playlist.html')

def play_song(request, song_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    email = request.session.get('user', {}).get('email')
    if not email:
        return redirect('authentication:login')

    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    cursor.execute(f"""
            INSERT INTO AKUN_PLAY_SONG (email_pemain, id_song, waktu)
            VALUES ('{email}','{song_id}','{current_timestamp}');
        """)

    connection.commit()
    messages.success(request, 'You\'ve successfully played the song.')
    
    referer_url = request.META.get('HTTP_REFERER', 'default_fallback_view_name')
    return redirect(referer_url)

def play_playlist(request, id_user_playlist):
    connection = get_db_connection()
    cursor = connection.cursor()
    email = request.session.get('user', {}).get('email')
    if not email:
        return redirect('authentication:login')

    cursor.execute(f"""
            SELECT email_pembuat
            FROM USER_PLAYLIST
            WHERE id_user_playlist = '{id_user_playlist}';
        """)

    email_pembuat = cursor.fetchall()[0][0]

    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    cursor.execute(f"""
            INSERT INTO AKUN_PLAY_USER_PLAYLIST (email_pemain, id_user_playlist, email_pembuat, waktu)
            VALUES ('{email}','{id_user_playlist}','{email_pembuat}','{current_timestamp}');
        """)

    connection.commit()
    messages.success(request, 'You\'ve successfully played the playlist.')
    
    referer_url = request.META.get('HTTP_REFERER', 'default_fallback_view_name')
    return redirect(referer_url)

def delete_playlist(request, playlist_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    email = request.session.get('user', {}).get('email')
    if not email:
        return redirect('authentication:login')

    cursor.execute(f"""
            DELETE FROM PLAYLIST WHERE id = '{playlist_id}';
        """)
    connection.commit()
    
    return redirect('playlist:show_playlist')

def edit_playlist(request, playlist_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    email = request.session.get('user', {}).get('email')
    if not email:
        return redirect('authentication:login')

    if request.method == 'POST':
        judul = request.POST.get('judul')
        deskripsi = request.POST.get('deskripsi')

        cursor.execute(f"""
                UPDATE USER_PLAYLIST 
                SET judul = '{judul}', deskripsi = '{deskripsi}' 
                WHERE id_playlist = '{playlist_id}';
            """)
        connection.commit()

        return redirect('playlist:show_playlist')
    
    context = {
        'id': playlist_id
    }
    return render(request, 'edit_playlist.html', context)

def add_to_playlist_from_song(request, song_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    email = request.session.get('user', {}).get('email')
    if not email:
        return redirect('authentication:login')

    if request.method == 'POST':
        playlist_id = request.POST.get('playlist')
        cursor = connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO playlist_song (id_playlist, id_song)
                VALUES (%s, %s);
                """, (str(playlist_id), song_id))
            connection.commit()
            messages.success(request, "Song added successfully to the playlist.")
        except UniqueViolation as e:
            print(e)
            connection.rollback()  # Rollback the transaction on error
            messages.error(request, "This song is already in the playlist.")
        except Exception as e:
            print(e)
            connection.rollback()  # Rollback the transaction on error
            messages.error(request, "An unexpected error occurred.")
        finally:
            cursor.close()
            connection.close()

        return redirect('playlist:user_playlist', playlist_id=playlist_id)

    cursor.execute(f"""
                SELECT 
                    k.judul, 
                    a.nama,
                    k.id
                FROM 
                    KONTEN AS k
                JOIN 
                    song AS s ON s.id_konten = k.id
                JOIN 
                    artist AS ar ON ar.id = s.id_artist
                JOIN 
                    akun AS a ON a.email = ar.email_akun
                WHERE 
                    s.id_konten = '{song_id}';
            """)
    connection.commit()

    res = cursor.fetchall()[0]
    context = {
        'judul': res[0],
        'artist': res[1],
        'id_song' : res[2]
    }

    cursor.execute(f"""
                SELECT up.id_playlist, up.judul
                FROM USER_PLAYLIST up
                JOIN AKUN a ON up.email_pembuat = a.email
                WHERE a.email = '{email}';
            """)
    connection.commit()

    result = cursor.fetchall()
    if result == []:
        messages.error(request, "You have no playlist.")

        return redirect('playlist:show_playlist')
        
    playlists = [{'id': str(data[0]), 'judul': data[1]} for data in result]
    context['playlists'] = playlists
    
    return render(request, 'add_to_playlist_from_song.html', context)