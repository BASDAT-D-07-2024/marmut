from django.shortcuts import render

# Create your views here.
def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

def register_user(request):
    return render(request, 'register-user.html')

def register_label(request):
    return render(request, 'register-label.html')