from django.shortcuts import render

def show_playlist(request):
    return render(request, "show_playlist.html")

def user_playlist(request):
    return render(request, "user_playlist.html")
