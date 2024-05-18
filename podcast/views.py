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
def play_podcast(request, id_konten):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    role = request.session.get('role')
    user = request.session.get('user')

    context = {
            'podcasts': [],
            'genres':[],
            'episodes': [],
        }
    
    try:
        connection = get_db_connection()      
        cursor = connection.cursor()
        
        cursor.execute('SELECT * FROM KONTEN WHERE id = %s', (id_konten,))
        podcast = cursor.fetchone()
        konversi_durasi_podcast = convert_duration(podcast[4])
        podcast_detail = {
            'judul_podcast': podcast[1],
            'tanggal_rilis': podcast[2],
            'tahun': podcast[3],
            'durasi': konversi_durasi_podcast,
        }
        context ['podcasts'] = podcast_detail

        cursor.execute('SELECT * FROM GENRE WHERE id_konten = %s', (id_konten,))
        genres = cursor.fetchall()

        for i in range (len(genres)):
            genre = {
                'genre': genres[i][1]
            }
            context['genres'].append(genre)
        
        cursor.execute('SELECT PODCAST.email_podcaster FROM PODCAST WHERE id_konten = %s', (id_konten,))
        email_podcaster = cursor.fetchone()

        cursor.execute('SELECT * FROM AKUN WHERE email = %s', (email_podcaster,))
        nama_podcaster = cursor.fetchone()

        context['nama'] = nama_podcaster[2]
        
        cursor.execute('SELECT * FROM EPISODE WHERE id_konten_podcast = %s', (id_konten,))
        episodes = cursor.fetchall()

        for i in range (len(episodes)):
            konversi_durasi_episode = convert_duration(episodes[i][4])
            episode = {
                'subjudul': episodes[i][2],
                'deskripsi': episodes[i][3],
                'durasi': konversi_durasi_episode,
                'tanggal': episodes[i][5],
            }
            context['episodes'].append(episode)

        return render(request, 'play_podcast.html', context)
    except psycopg2.Error as error:
        messages.error(request, 'Error while fetching data from database')
        return render(request, 'play_podcast.html', context)
    finally:
        if connection:
            cursor.close()
            connection.close()

def create_podcast(request):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    role = request.session.get('role')
    user = request.session.get('user')
    
    if request.method == 'POST':
        judul_podcast = request.POST.get('judul_podcast')
        genre = request.POST.getlist('genre')
        durasi = request.POST.get('durasi')

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            id_podcast = uuid.uuid4()
            tanggal_rilis, tahun = today_date()
            cursor.execute('INSERT INTO KONTEN (id, judul, tanggal_rilis, tahun, durasi) VALUES (%s, %s, %s, %s, %s)', (id_podcast, judul_podcast, tanggal_rilis, tahun, durasi))
            connection.commit()

            cursor.execute('INSERT INTO PODCAST (id_konten, email_podcaster) VALUES (%s, %s)', (id_podcast, user['email']))
            connection.commit()

            for i in range(len(genre)):
                cursor.execute('INSERT INTO GENRE (id_konten, genre) VALUES (%s, %s)', (id_podcast, genre[i]))
                connection.commit()

            messages.success(request, 'Podcast created successfully')
            return redirect('podcast:list_podcast')
        except psycopg2.Error as error:
            messages.error(request, 'Error while inserting data to database')
            return redirect('podcast:create_podcast')
        finally:
            if connection:
                cursor.close()
                connection.close()

    if 'podcaster' in role:
        try:
            context = fetch_data_for_create_ep(role, user)
            return render(request, 'create_podcast.html', context)
        except psycopg2.Error as error:
            messages.error(request, 'Error while fetching data from database')
            return render(request, 'create_podcast.html')

    return redirect('main:dashboard')

def create_ep_podcast(request, id_konten):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    role = request.session.get('role')
    user = request.session.get('user')

    if 'podcaster' not in role:
        return redirect('main:dashboard')
    
    if request.method == 'POST':
        judul_ep = request.POST.get('judul_ep')
        deskripsi = request.POST.get('deskripsi')
        durasi = request.POST.get('durasi')

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            id_episode = uuid.uuid4()
            tanggal_rilis = today_date_no_year()
            cursor.execute('INSERT INTO EPISODE (id_episode, id_konten_podcast, judul, deskripsi, durasi, tanggal_rilis) VALUES (%s, %s, %s, %s, %s, %s)', (id_episode, id_konten, judul_ep, deskripsi, durasi, tanggal_rilis))
            connection.commit()

            messages.success(request, 'Episode created successfully')
            return redirect('podcast:list_ep_podcast', id_konten=id_konten)
        except psycopg2.Error as error:
            messages.error(request, 'Error while inserting data to database')
            return redirect('podcast:create_ep_podcast', id_konten=id_konten)
        finally:
            if connection:
                cursor.close()
                connection.close()

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        context = fetch_data_for_create_ep(role, user)
        cursor.execute('SELECT * FROM KONTEN WHERE id = %s', (id_konten,))
        judul_podcast = cursor.fetchone()
        judul_podcast = {
            'id': id_konten,
            'judul': judul_podcast[1],
        }
        context['judul_podcast'] = judul_podcast

        return render(request, 'create_ep_podcast.html', context)
    except psycopg2.Error as error:
        messages.error(request, 'Error while fetching data from database')
        return render(request, 'create_ep_podcast.html')
    finally:
        if connection:
            cursor.close()
            connection.close()

def list_podcast(request):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    role = request.session.get('role')
    user = request.session.get('user')

    context = {
        'konten': [],
        'is_podcaster': 'podcaster' in role,
    }

    if 'podcaster' in role:
        try:
            connection = get_db_connection()      
            cursor = connection.cursor()
            
            cursor.execute('''
                SELECT KONTEN.id, KONTEN.judul, COUNT(EPISODE.id_episode) AS jumlah_episode, 
                       COALESCE(SUM(EPISODE.durasi), 0) AS total_durasi
                FROM PODCAST 
                JOIN KONTEN ON PODCAST.id_konten = KONTEN.id
                LEFT JOIN EPISODE ON KONTEN.id = EPISODE.id_konten_podcast
                WHERE PODCAST.email_podcaster = %s
                GROUP BY KONTEN.id
            ''', (user['email'],))
            konten = cursor.fetchall()

            for i in range(len(konten)):
                konversi_total_durasi = convert_duration(konten[i][3])
                podcast = {
                    'id': konten[i][0],
                    'judul': konten[i][1],
                    'jumlah_episode': konten[i][2],
                    'total_durasi': konversi_total_durasi,
                }
                context['konten'].append(podcast)

            return render(request, 'list_podcast.html', context)
        except psycopg2.Error as error:
            messages.error(request, 'Error while fetching data from database')
            return render(request, 'list_podcast.html', context)
        finally:
            if connection:
                cursor.close()
                connection.close()
    return redirect('main:dashboard')

def list_ep_podcast(request, id_konten):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    role = request.session.get('role')

    context = {
        'id': id_konten,
        'episodes': [],
    }

    if 'podcaster' in role:
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute('SELECT * FROM KONTEN WHERE id = %s', (id_konten,))
            podcast = cursor.fetchone()
            context['judul'] = podcast[0]

            cursor.execute('SELECT * FROM EPISODE WHERE id_konten_podcast = %s', (id_konten,))
            episode_podcast = cursor.fetchall()

            for i in range(len(episode_podcast)):
                konversi_durasi_ep = convert_duration(episode_podcast[i][4])
                episode = {
                    'id': episode_podcast[i][0],
                    'judul_episode': episode_podcast[i][2],
                    'deskripsi': episode_podcast[i][3],
                    'durasi': konversi_durasi_ep,
                    'tanggal': episode_podcast[i][5],
                }
                context['episodes'].append(episode)

            return render(request, 'list_ep_podcast.html', context)
        except psycopg2.Error as error:
            messages.error(request, 'Error while fetching data from database')
            return render(request, 'list_ep_podcast.html')
        finally:
            if connection:
                cursor.close()
                connection.close()
    return redirect('main:dashboard')

def delete_podcast(request, id_konten):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    if request.method != 'DELETE':
        return JsonResponse({'message': 'Method not allowed'}, status=405)

    role = request.session.get('role')

    if 'podcaster' in role:
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute('SELECT * FROM KONTEN WHERE id = %s', (id_konten,))
            konten = cursor.fetchone()

            if konten is None:
                return JsonResponse({'message': 'Podcast not found'}, status=404)
            else:
                cursor.execute('DELETE FROM KONTEN WHERE id = %s', (id_konten,))
                connection.commit()
            
            return JsonResponse({'message': 'Podcast deleted successfully'}, status=200)
        except psycopg2.Error as error:
            return JsonResponse({'message': 'Error while deleting podcast'}, status=500)
        finally:
            if connection:
                cursor.close()
                connection.close()

def delete_ep(request, id_episode):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    if request.method != 'DELETE':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    
    role = request.session.get('role')

    if 'podcaster' in role:
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute('SELECT * FROM EPISODE WHERE id = %s', (id_episode,))
            episode = cursor.fetchone()

            if episode is None:
                return JsonResponse({'message': 'Episode not found'}, status=404)
            else:
                cursor.execute('DELETE FROM EPISODE WHERE id = %s', (id_episode,))
                connection.commit()

            return JsonResponse({'message': 'Episode deleted successfully'}, status=200)
        except psycopg2.Error as error:
            print(error)
            return JsonResponse({'message': 'Error while deleting episode'}, status=500)
        finally:
            if connection:
                cursor.close()
                connection.close()

def today_date_no_year():
    today = date.today()
    return (today.strftime('%Y-%m-%d'))

def convert_duration(minutes):
    if minutes < 60:
        return f"{minutes} menit"
    hours = minutes // 60
    remaining_minutes = minutes % 60
    return f"{hours} jam {remaining_minutes} menit" if remaining_minutes else f"{hours} jam"

def fetch_data_for_create_ep(role, user):
    context = {
        'is_podcaster': 'podcaster' in role,
        'podcasters': [],
        'genres': [],
    }

    if 'podcaster' in role:
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Get podcaster
            # cursor.execute('SELECT * FROM PODCAST WHERE email_podcaster = %s' (user['email'],))
            # podcaster = cursor.fetchone()
            # context['podcaster'] = {
            #     'id_podcast': podcaster[0],
            #     'email_podcaster': podcaster[1],
            #     'nama': user['nama'],
            # }

            # Get all genres
            cursor.execute('SELECT DISTINCT on (genre) * FROM GENRE')
            genres = cursor.fetchall()
            for i in range(len(genres)):
                genre = {
                    'id': genres[i][0],
                    'genre': genres[i][1],
                }
                context['genres'].append(genre)
            
            return context
        except psycopg2.Error as error:
            raise error('Error while fetching data from database')
            
        finally:
            if connection:
                cursor.close()
                connection.close()