def username(request):
    return {'username': request.session.get('username', 'Guest')}

def role(request):
    return {'role': request.session.get('role', 'Guest')}