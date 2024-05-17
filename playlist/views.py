from django.shortcuts import render, redirect
from django.db import connection
from django.http import HttpResponse
from playlist.views import *

def show_playlist(request):
    if request.session.get('role') is None:
        return redirect('authentication:login')

    user = request.session.get('user')
    email = user['email']

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT up.judul, up.jumlah_lagu, up.total_durasi, up.id_user_playlist
            FROM USER_PLAYLIST up
            JOIN AKUN a ON up.email_pembuat = a.email
            JOIN PLAYLIST p ON up.id_playlist = p.id
            WHERE a.email = %s
        """, [email])

        hasil_playlist = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
        print(hasil_playlist)

    context = {
        "user": user,
        "playlist": hasil_playlist,
    }

    print(context)

    return render(request, "show_playlist.html", context)

def user_playlist(request, playlist_id):
    if request.session.get('role') is None:
        return redirect('authentication:login')

    email = request.session.get('user', {}).get('email')
    if not email:
        return redirect('authentication:login')  # Redirect jika tidak ada email di session

    songs = []
    with connection.cursor() as cursor:
        # Execute your provided query
        cursor.execute("""
        SELECT k.id, k.judul, n.nama, k.durasi
        FROM song s
        JOIN artist a ON s.id_artist = a.id
        JOIN akun n ON a.email_akun = n.email
        JOIN playlist_song ps ON s.id_konten = ps.id_song
        JOIN konten k ON s.id_konten = k.id
        JOIN user_playlist up ON a.email_akun = n.email
        WHERE up.email_pembuat = %s AND up.id_user_playlist = %s;
        """, [email, playlist_id])
        
        # Fetch all song details for the playlist
        rows = cursor.fetchall()
        if not rows:
            return HttpResponse("Playlist not found or contains no songs", status=404)

        # Process each row into a dictionary and append to the songs list
        for row in rows:
            song_dict = {
                'id': row[0],
                'judul': row[1],
                'nama_artis': row[2],
                'durasi': row[3]
            }
            songs.append(song_dict)

    # Prepare context with user and playlist details
    context = {
        "user": request.session.get('user'),
        "songs": songs,  # Update context key to 'songs' for consistency with template usage
        "playlist_id": playlist_id
    }

    return render(request, "user_playlist.html", context)

def delete_song(request, song_id):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    if request.method != 'DELETE':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    
    role = request.session.get('role')

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM SONG WHERE id_konten = %s', (song_id,))
        song = cursor.fetchone()

        if song is None:
            return JsonResponse({'message': 'Song not found'}, status=404)
        
        cursor.execute('DELETE FROM SONG WHERE id_konten = %s', (song_id,))
        connection.commit()
        
        cursor.execute('DELETE FROM KONTEN WHERE id = %s', (song_id,))
        connection.commit()

        return JsonResponse({'message': 'Song deleted successfully'}, status=200)
    except psycopg2.Error as error:
        print(error)
        return JsonResponse({'message': 'Error while deleting song'}, status=500)
    finally:
        if connection:
            cursor.close()
            connection.close()

# def add_song(request, playlist_id):
#     if request.method == 'POST':
#         # Handle the form submission
#         selected_song_id = request.POST.get('song')

#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("""
#                     INSERT INTO playlist_song (id_playlist, id_song)
#                     VALUES (%s, %s)
#                 """, [playlist_id, selected_song_id])
#             return redirect('user_playlist', playlist_id=playlist_id)
#         except psycopg2.Error as error:
#             print(error)
#             return HttpResponse("Error while adding song to playlist", status=500)
    
#     # Fetch all songs from the database using raw SQL
#     songs = []
#     with connection.cursor() as cursor:
#         cursor.execute("""
#             SELECT s.id_konten, k.judul, a.nama
#             FROM song s
#             JOIN konten k ON s.id_konten = k.id
#             JOIN artist a ON s.id_artist = a.id
#         """)
#         rows = cursor.fetchall()
#         for row in rows:
#             song = {
#                 'id': row[0],
#                 'judul': row[1],
#                 'artist': row[2]
#             }
#             songs.append(song)
    
#     return render(request, 'add_song.html', {'songs': songs, 'playlist_id': playlist_id})


def view_song(request):
    return render(request, 'view_song.html')

def create_playlist(request):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    if request.method == 'POST':
        judul_playlist = request.POST.get('judul_playlist')
        deskripsi = request.POST.get('deskripsi')
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        id_playlist = uuid.uuid4()
        cursor.execute('INSERT INTO PLAYLIST (id, deskripsi) VALUES (%s, %s)')
        connection.commit()
    except psycopg2.Error as error:
        messages.error(request, 'Error while inserting data to database')
        return redirect('playlist:create_playlist')
    finally:
        if connection:
            cursor.close()
            connection.close()
    return render('show_playlist.html')