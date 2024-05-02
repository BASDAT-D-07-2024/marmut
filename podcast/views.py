from django.shortcuts import render

# Create your views here.
def play_podcast(request):

    return render(request, "play_podcast.html")