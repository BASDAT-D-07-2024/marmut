from django.shortcuts import render
import uuid
import psycopg2
from datetime import date
from django.contrib import messages
from django.http import JsonResponse
from utils.db_utils import get_db_connection
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache

# Create your views here.
def show_song(request):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    role = request.session.get('role')
    user = request.session.get('user')

    connection = get_db_connection()      
    cursor = connection.cursor()


    context = {
        ""
    }

    return render(request, "show_song.html")