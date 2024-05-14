from django.shortcuts import render

# Create your views here.
def show_song(request):
    return render(request, "show_song.html")