from django.shortcuts import render

def list_album(request):
    return render(request, 'list-album.html')

def view_album(request, id):
    context = {
        'id': id,
    }
    return render(request, 'view-album.html', context)
