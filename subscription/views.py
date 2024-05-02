from django.shortcuts import render

# Create your views here.
def subs_page(request):
    return render(request, 'subs-page.html')