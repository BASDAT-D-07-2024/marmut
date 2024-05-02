from django.shortcuts import render

# Create your views here.
def list_download(request):
    return render(request, 'list-download.html')