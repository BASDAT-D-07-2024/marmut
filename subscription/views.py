import uuid
import psycopg2
from django.contrib import messages
from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from utils.db_utils import get_db_connection

# Create your views here.
def subs_page(request):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    role = request.session.get('role')
    user = request.session.get('user')

    context = {
        'subscriptions': []
    }

    if 'label' not in role:
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute('SELECT * FROM paket')
            subscriptions = cursor.fetchall()
            for subscription in subscriptions:
                sub = {
                    'jenis': subscription[0],
                    'harga': format_rupiah(subscription[1]),
                }
                context['subscriptions'].append(sub)
        except psycopg2.Error:
            messages.error(request, 'Error while fetching data from database')
        finally:
            cursor.close()
            connection.close()
    return render(request, 'subs-page.html', context)

def checkout(request, jenis_paket):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    role = request.session.get('role')
    user = request.session.get('user')

    if 'label' not in role:
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            if request.method == 'POST':
                id = uuid.uuid4()
                jenis_paket = request.POST.get('jenis_paket')
                email = user['email'] 
                timestamp_dimulai = datetime.now()
                timestamp_berakhir = update_timestamp(timestamp_dimulai, jenis_paket)
                metode_bayar = request.POST.get('metode_pembayaran')
                nominal = reverse_format_rupiah(request.POST.get('nominal'))

                query = f"""
                    SELECT * FROM paket WHERE jenis = '{jenis_paket}'
                """
                cursor.execute(query)
                paket = cursor.fetchone()
                if paket is None:
                    messages.error(request, 'Paket not found')
                    return redirect('subscription:subscriptions')

                cursor.execute('INSERT INTO transaction (id, jenis_paket, email, timestamp_dimulai, timestamp_berakhir, metode_bayar, nominal) VALUES (%s, %s, %s, %s, %s, %s, %s)', (id, jenis_paket, email, timestamp_dimulai, timestamp_berakhir, metode_bayar, nominal))
                connection.commit()
                cursor.execute('DELETE FROM NONPREMIUM WHERE email = %s', (email,))
                connection.commit()
                cursor.execute('INSERT INTO PREMIUM (email) VALUES (%s)', (email,))
                connection.commit()
                messages.success(request, 'Subscription successful!')
            else:
                query = f"""
                    SELECT * FROM paket WHERE jenis = '{jenis_paket}'
                """
                cursor.execute(query)
                paket = cursor.fetchone()
                if paket is None:
                    messages.error(request, 'Paket not found')
                    return redirect('subscription:subscriptions')
                context = {
                    'jenis': paket[0],
                    'harga': format_rupiah(paket[1]),
                }
                return render(request, 'checkout.html', context)
        except psycopg2.Error as e:
            messages.error(request, str(e).splitlines()[0])
            return redirect('subscription:checkout', jenis_paket=jenis_paket)
        finally:
            cursor.close()
            connection.close()

    return redirect('subscription:subscriptions')

def history(request):
    if request.session.get('role') is None:
        return redirect('authentication:login')
    
    role = request.session.get('role')
    user = request.session.get('user')

    context = {
        'transactions': []
    }

    if 'label' not in role:
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute('SELECT * FROM transaction WHERE email = %s', (user['email'],))
            transactions = cursor.fetchall()
            for transaction in transactions:
                riwayat = {
                    'id': transaction[0],
                    'jenis_paket': transaction[1],
                    'timestamp_dimulai': transaction[3],
                    'timestamp_berakhir': transaction[4],
                    'metode_pembayaran': transaction[5],
                    'nominal': format_rupiah(transaction[6]),
                }
                context['transactions'].append(riwayat)
        except psycopg2.Error:
            messages.error(request, 'Error while fetching data from database')
        finally:
            cursor.close()
            connection.close()
    return render(request, 'history.html', context)


def format_rupiah(amount):
    # Convert the amount to an integer (if it's not already)
    amount = int(amount)
    
    # Format the number with commas as thousand separators
    formatted_amount = f"{amount:,.0f}"
    
    # Replace commas with dots
    formatted_amount = formatted_amount.replace(",", ".")
    
    # Add the "Rp" prefix
    return f"Rp{formatted_amount}"

def reverse_format_rupiah(formatted_amount):
    # Convert the formatted amount to a string (if it's not already)
    formatted_amount = str(formatted_amount)

    # Remove the "Rp" prefix
    if formatted_amount.startswith("Rp"):
        formatted_amount = formatted_amount[2:]
    
    # Replace dots with commas (if necessary)
    formatted_amount = formatted_amount.replace(".", "")
    
    # Convert the cleaned string to an integer
    amount = int(formatted_amount)
    
    return amount

def update_timestamp(timestamp, jenis):    
    if jenis == "1 bulan":
        timestamp += timedelta(days=30)
    elif jenis == "3 bulan":
        timestamp += timedelta(days=90)
    elif jenis == "6 bulan":
        timestamp += timedelta(days=180)
    elif jenis == "1 tahun":
        timestamp += timedelta(days=365)
    
    return timestamp