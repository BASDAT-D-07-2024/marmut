from django.shortcuts import render, redirect

def dashboard(request):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    role = request.session.get('role')
    user = request.session.get('user')
    
    if 'label' in role:
        return render(request, 'dashboard-label.html', user)
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
