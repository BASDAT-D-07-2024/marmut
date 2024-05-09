from django.shortcuts import render

def dashboard(request):
    role = request.session.get('role')
    user = request.session.get('user')
    
    if 'label' in role:
        context = {
            'nama': user['nama'],
            'email': user['email'],
            'kontak': user['kontak']
        }
        return render(request, 'dashboard-label.html', context)
    else:
        roles_capitalized = [role.capitalize() for role in role]
        roles_string = ', '.join(roles_capitalized)
        
        context = {
            'is_podcaster': 'podcaster' in role,
            'is_artist': 'artist' in role,
            'is_songwriter': 'songwriter' in role,
            'roles': roles_string,
            'email': user['email'],
            'nama': user['nama'],
            'gender': user['gender'],
            'tempat_lahir': user['tempat_lahir'],
            'tanggal_lahir': user['tanggal_lahir'],
            'is_verified': user['is_verified'],
            'kota_asal': user['kota_asal']
        }

        return render(request, 'dashboard.html', context)
