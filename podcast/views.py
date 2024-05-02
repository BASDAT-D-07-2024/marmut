from django.shortcuts import render

# Create your views here.
def play_podcast(request):

    return render(request, "play_podcast.html")

def create_podcast(request):

    return render(request, "create_podcast.html")

def create_ep_podcast(request):

    return render(request, "create_ep_podcast.html")

def list_podcast(request):

    return render(request, "list_podcast.html")

def list_ep_podcast(request):

    return render(request, "list_ep_podcast.html")