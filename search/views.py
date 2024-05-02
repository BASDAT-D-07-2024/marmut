from django.shortcuts import render

# Create your views here.
def search_result(request):
    return render(request, 'search-result.html')