from django.contrib import admin
from .models import Category, MenuItem, Table, Order, OrderItem, Reservation
from django.utils import timezone
from datetime import datetime, timedelta
from django import forms
from django.utils.html import format_html

class TableAdminForm(forms.ModelForm):
    check_date = forms.DateField(required=False, label='Tarih Seç')
    check_time = forms.TimeField(required=False, label='Saat Seç')

    class Meta:
        model = Table
        fields = '__all__'

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    form = TableAdminForm
    list_display = ('number', 'capacity', 'min_chairs', 'max_chairs', 'get_status', 'get_current_reservation')
    list_filter = ('capacity',)
    search_fields = ('number',)
    ordering = ('number',)
    change_list_template = 'admin/table_change_list.html'

    def get_status(self, obj):
        if obj.is_occupied:
            return '🟡 Dolu'
        return '🟢 Müsait'
    get_status.short_description = 'Durum'

    def get_current_reservation(self, obj):
        if obj.is_occupied and hasattr(obj, 'current_reservation'):
            return f"{obj.current_reservation.customer_name} - {obj.current_reservation.time}"
        return '-'
    get_current_reservation.short_description = 'Mevcut Rezervasyon'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        if request.method == 'POST':
            check_date = request.POST.get('check_date')
            check_time = request.POST.get('check_time')
            if check_date and check_time:
                try:
                    check_datetime = datetime.strptime(f"{check_date} {check_time}", '%Y-%m-%d %H:%M')
                    time_window_start = (check_datetime - timedelta(hours=1)).time()
                    time_window_end = (check_datetime + timedelta(hours=1)).time()
                    
                    # Eğer zaman dilimi gece yarısını geçiyorsa
                    if time_window_start > time_window_end:
                        reservations = Reservation.objects.filter(
                            date=check_datetime.date(),
                            time__gte=time_window_start,
                            status__in=['pending', 'confirmed']
                        ) | Reservation.objects.filter(
                            date=check_datetime.date() + timedelta(days=1),
                            time__lte=time_window_end,
                            status__in=['pending', 'confirmed']
                        )
                    else:
                        reservations = Reservation.objects.filter(
                            date=check_datetime.date(),
                            time__gte=time_window_start,
                            time__lte=time_window_end,
                            status__in=['pending', 'confirmed']
                        )
                    
                    occupied_tables = reservations.values_list('table_id', flat=True)
                    extra_context['occupied_tables'] = list(occupied_tables)
                    extra_context['check_date'] = check_date
                    extra_context['check_time'] = check_time
                except ValueError:
                    pass
        
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'table', 'date', 'time', 'number_of_guests', 'status', 'created_at')
    list_filter = ('status', 'date', 'table')
    search_fields = ('customer_name', 'customer_email', 'customer_phone')
    date_hierarchy = 'date'
    ordering = ('-date', '-time')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available')
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_available')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'table', 'created_at', 'get_total')
    list_filter = ('created_at',)
    search_fields = ('table__number',)
    
    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = 'Toplam Tutar'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'menu_item', 'quantity', 'price', 'get_subtotal')
    list_filter = ('menu_item__category',)
    search_fields = ('menu_item__name',)
    
    def get_subtotal(self, obj):
        return obj.get_subtotal()
    get_subtotal.short_description = 'Ara Toplam'

# Örnek verileri oluşturmak için
def create_sample_data():
    # Kategoriler
    categories = {
        'Çorbalar': 'Özenle hazırlanmış ev yapımı çorbalarımız',
        'Başlangıçlar': 'Lezzetli başlangıçlar ve mezeler',
        'Ana Yemekler': 'Özel soslar ve taze malzemelerle hazırlanan ana yemekler',
        'Izgaralar': 'Özel baharatlarla marine edilmiş ızgara çeşitleri',
        'Tatlılar': 'Ev yapımı özel tatlılarımız',
        'İçecekler': 'Soğuk ve sıcak içecek çeşitleri'
    }
    
    for name, desc in categories.items():
        Category.objects.get_or_create(name=name, defaults={'description': desc})
    
    # Menü öğeleri
    menu_items = [
        # Çorbalar
        {'name': 'Mercimek Çorbası', 'category': 'Çorbalar', 'price': 45, 'description': 'Geleneksel tarifimizle hazırlanan ev yapımı mercimek çorbası'},
        {'name': 'Ezogelin Çorbası', 'category': 'Çorbalar', 'price': 45, 'description': 'Özel baharatlarla zenginleştirilmiş ezogelin çorbası'},
        {'name': 'Yayla Çorbası', 'category': 'Çorbalar', 'price': 45, 'description': 'Yoğurt ve pirinç ile hazırlanan geleneksel yayla çorbası'},
        
        # Başlangıçlar
        {'name': 'Humus', 'category': 'Başlangıçlar', 'price': 65, 'description': 'Nohut püresi, tahin ve zeytinyağı ile hazırlanan humus'},
        {'name': 'Patlıcan Ezme', 'category': 'Başlangıçlar', 'price': 65, 'description': 'Közlenmiş patlıcan ve özel baharatlarla hazırlanan ezme'},
        {'name': 'Zeytinyağlı Yaprak Sarma', 'category': 'Başlangıçlar', 'price': 75, 'description': 'El açması yaprak sarma, pirinç ve baharatlarla'},
        
        # Ana Yemekler
        {'name': 'Kuzu Tandır', 'category': 'Ana Yemekler', 'price': 180, 'description': 'Özel baharatlarla marine edilmiş kuzu tandır'},
        {'name': 'Mantı', 'category': 'Ana Yemekler', 'price': 120, 'description': 'El açması mantı, yoğurt ve naneli sos ile'},
        {'name': 'Karnıyarık', 'category': 'Ana Yemekler', 'price': 110, 'description': 'Kıymalı karnıyarık, közlenmiş patlıcan ile'},
        
        # Izgaralar
        {'name': 'Adana Kebap', 'category': 'Izgaralar', 'price': 160, 'description': 'Özel baharatlarla hazırlanan Adana kebap'},
        {'name': 'Piliç Şiş', 'category': 'Izgaralar', 'price': 140, 'description': 'Marine edilmiş piliç şiş, özel sos ile'},
        {'name': 'Kuzu Pirzola', 'category': 'Izgaralar', 'price': 200, 'description': 'Özel baharatlarla marine edilmiş kuzu pirzola'},
        
        # Tatlılar
        {'name': 'Künefe', 'category': 'Tatlılar', 'price': 85, 'description': 'Antep fıstıklı özel künefe'},
        {'name': 'Sütlaç', 'category': 'Tatlılar', 'price': 65, 'description': 'Fırında pişirilmiş ev yapımı sütlaç'},
        {'name': 'Baklava', 'category': 'Tatlılar', 'price': 95, 'description': '40 kat el açması baklava'},
        
        # İçecekler
        {'name': 'Türk Kahvesi', 'category': 'İçecekler', 'price': 35, 'description': 'Geleneksel Türk kahvesi'},
        {'name': 'Ayran', 'category': 'İçecekler', 'price': 25, 'description': 'Ev yapımı ayran'},
        {'name': 'Taze Sıkılmış Portakal Suyu', 'category': 'İçecekler', 'price': 45, 'description': 'Taze sıkılmış portakal suyu'}
    ]
    
    for item in menu_items:
        category = Category.objects.get(name=item['category'])
        MenuItem.objects.get_or_create(
            name=item['name'],
            category=category,
            defaults={
                'price': item['price'],
                'description': item['description'],
                'is_available': True
            }
        )

# Örnek verileri oluştur
create_sample_data()
