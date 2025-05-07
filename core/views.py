from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, MenuItem, Table, Order, OrderItem, Reservation
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

def home(request):
    categories = Category.objects.all()
    return render(request, 'core/home.html', {'categories': categories})

def menu(request):
    categories = Category.objects.all()
    menu_items = MenuItem.objects.filter(is_available=True)
    return render(request, 'core/menu.html', {
        'categories': categories,
        'menu_items': menu_items
    })

@login_required
def table_list(request):
    # Sadece rezervasyon sisteminde kullanılan masaları getir (4, 6 ve 10 kişilik masalar)
    tables = Table.objects.filter(capacity__in=[4, 6, 10]).order_by('number')
    
    # Tarih ve saat parametrelerini al
    check_date = request.GET.get('date')
    check_time = request.GET.get('time')
    
    if check_date and check_time:
        try:
            # Tarih ve saati birleştir
            datetime_str = f"{check_date} {check_time}"
            check_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
            
            # 2 saatlik zaman dilimini hesapla
            time_window_start = (check_datetime - timedelta(hours=1)).time()
            time_window_end = (check_datetime + timedelta(hours=1)).time()
            
            # Seçilen tarih ve 2 saatlik zaman dilimi içinde dolu olan masaları bul
            occupied_tables = Reservation.objects.filter(
                date=check_datetime.date(),
                time__gte=time_window_start,
                time__lte=time_window_end,
                status__in=['pending', 'confirmed']
            ).values_list('table_id', flat=True)
            
            # Her masa için durumu güncelle
            for table in tables:
                table.is_occupied = table.id in occupied_tables
                
                # Mevcut rezervasyonu bul
                if table.is_occupied:
                    table.current_reservation = Reservation.objects.filter(
                        table=table,
                        date=check_datetime.date(),
                        time__gte=time_window_start,
                        time__lte=time_window_end,
                        status__in=['pending', 'confirmed']
                    ).first()
                else:
                    table.current_reservation = None
                    
        except ValueError:
            pass
    
    return render(request, 'core/table_list.html', {
        'tables': tables,
        'selected_date': check_date,
        'selected_time': check_time
    })

@login_required
def create_order(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    if request.method == 'POST':
        order = Order.objects.create(table=table)
        menu_items = request.POST.getlist('menu_items')
        quantities = request.POST.getlist('quantities')
        
        for item_id, quantity in zip(menu_items, quantities):
            if int(quantity) > 0:  # Sadece miktarı 0'dan büyük olan ürünleri ekle
                menu_item = get_object_or_404(MenuItem, id=item_id)
                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=int(quantity),
                    price=menu_item.price
                )
        
        messages.success(request, 'Sipariş başarıyla oluşturuldu.')
        return redirect('core:order_detail', order_id=order.id)
    
    menu_items = MenuItem.objects.filter(is_available=True)
    return render(request, 'core/create_order.html', {
        'table': table,
        'menu_items': menu_items
    })

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'core/order_detail.html', {'order': order})

def reservation(request):
    if request.method == 'POST':
        table_id = request.POST.get('table_id')
        number_of_guests = request.POST.get('number_of_guests')
        date = request.POST.get('date')
        time = request.POST.get('time')
        
        if not all([table_id, number_of_guests, date, time]):
            messages.error(request, 'Lütfen tüm alanları doldurun.')
            return redirect('core:reservation')
        
        table = get_object_or_404(Table, id=table_id)
        
        # Kişi sayısı kontrolü
        number_of_guests = int(number_of_guests)
        if number_of_guests < table.min_chairs or number_of_guests > table.max_chairs:
            messages.error(request, f'Bu masa için kişi sayısı {table.min_chairs} ile {table.max_chairs} arasında olmalıdır.')
            return redirect('core:reservation')
        
        # Tarih ve saat kontrolü
        try:
            reservation_date = datetime.strptime(date, '%Y-%m-%d').date()
            reservation_time = datetime.strptime(time, '%H:%M').time()
            
            if reservation_date < timezone.now().date():
                messages.error(request, 'Geçmiş bir tarih seçemezsiniz.')
                return redirect('core:reservation')
            
            # 2 saatlik zaman dilimini hesapla
            time_window_start = (datetime.combine(reservation_date, reservation_time) - timedelta(hours=1)).time()
            time_window_end = (datetime.combine(reservation_date, reservation_time) + timedelta(hours=1)).time()
            
            # Aynı masa için 2 saatlik zaman dilimi içinde başka rezervasyon var mı kontrol et
            existing_reservation = Reservation.objects.filter(
                table=table,
                date=reservation_date,
                time__gte=time_window_start,
                time__lte=time_window_end,
                status__in=['pending', 'confirmed']
            ).exists()
            
            if existing_reservation:
                messages.error(request, 'Seçilen masa ve saat için başka bir rezervasyon bulunmaktadır. Lütfen farklı bir saat seçin.')
                return redirect('core:reservation')
            
        except ValueError:
            messages.error(request, 'Geçersiz tarih veya saat formatı.')
            return redirect('core:reservation')
        
        try:
            reservation = Reservation.objects.create(
                customer_name=request.POST.get('customer_name'),
                customer_email=request.POST.get('customer_email'),
                customer_phone=request.POST.get('customer_phone'),
                table=table,
                number_of_guests=number_of_guests,
                date=reservation_date,
                time=reservation_time,
                notes=request.POST.get('notes')
            )
            messages.success(request, 'Rezervasyonunuz başarıyla oluşturuldu.')
            return redirect('core:home')
        except Exception as e:
            messages.error(request, 'Rezervasyon oluşturulurken bir hata oluştu.')
            return redirect('core:reservation')
    
    # Sadece rezervasyon sisteminde kullanılan masaları getir (4, 6 ve 10 kişilik masalar)
    tables = Table.objects.filter(capacity__in=[4, 6, 10]).order_by('number')
    return render(request, 'core/reservation.html', {'tables': tables})

@require_http_methods(["GET"])
def check_table_availability(request):
    date = request.GET.get('date')
    time = request.GET.get('time')
    
    if not date or not time:
        return JsonResponse({'error': 'Tarih ve saat gerekli'}, status=400)
    
    try:
        # Tarih ve saati birleştir
        datetime_str = f"{date} {time}"
        reservation_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
        
        # 2 saatlik zaman dilimini hesapla
        time_window_start = (datetime.combine(reservation_datetime.date(), reservation_datetime.time()) - timedelta(hours=1)).time()
        time_window_end = (datetime.combine(reservation_datetime.date(), reservation_datetime.time()) + timedelta(hours=1)).time()
        
        # Seçilen tarih ve 2 saatlik zaman dilimi içinde dolu olan masaları bul
        occupied_tables = Reservation.objects.filter(
            date=reservation_datetime.date(),
            time__gte=time_window_start,
            time__lte=time_window_end,
            status__in=['pending', 'confirmed']  # Hem bekleyen hem onaylanmış rezervasyonları kontrol et
        ).values_list('table_id', flat=True)
        
        occupied_tables_list = list(occupied_tables)
        print(f"Tarih: {date}, Saat: {time}")
        print(f"Dolu masalar: {occupied_tables_list}")
        
        return JsonResponse({
            'occupied_tables': occupied_tables_list,
            'date': date,
            'time': time
        })
    except Exception as e:
        print(f"Hata: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if request.method == 'POST':
        reservation.status = 'cancelled'
        reservation.save()
        messages.success(request, 'Rezervasyon başarıyla iptal edildi.')
        return redirect('core:table_list')
    
    return render(request, 'core/cancel_reservation.html', {
        'reservation': reservation
    })
