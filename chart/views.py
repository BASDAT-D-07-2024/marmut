from django.shortcuts import render

# Create your views here.
def chart_list(request):

    return render(request, "chart_list.html")

def chart_detail(request):

    return render(request, "chart_detail.html")