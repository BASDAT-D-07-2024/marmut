import psycopg2
from utils.db_utils import get_db_connection
from django.shortcuts import render, redirect

def dashboard(request):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    role = request.session.get('role')
    user = request.session.get('user')
    
    if 'label' in role:
        context = {
            'albums': [],
        }
        context.update(user)

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

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
        except psycopg2.Error as e:
            print(e)
        finally:
            if connection:
                cursor.close()
                connection.close()

        return render(request, 'dashboard-label.html', context)
    else:
        roles_capitalized = [role.capitalize() for role in role]
        roles_string = ', '.join(roles_capitalized)
  
        context = {
            'is_podcaster': 'podcaster' in role,
            'is_artist': 'artist' in role,
            'is_songwriter': 'songwriter' in role,
            'roles': roles_string,
        }
        context.update(user)

        return render(request, 'dashboard.html', context)
