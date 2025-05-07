from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class MenuItem(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    image = models.ImageField(upload_to='menu_items/', null=True, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Table(models.Model):
    number = models.IntegerField(unique=True)
    capacity = models.IntegerField(validators=[MinValueValidator(2), MaxValueValidator(12)])
    current_chairs = models.IntegerField(default=2)
    min_chairs = models.IntegerField(default=2)
    max_chairs = models.IntegerField(default=12)
    
    def __str__(self):
        return f"Masa {self.number}"

    def can_add_chair(self):
        return self.current_chairs < self.max_chairs

    def can_remove_chair(self):
        return self.current_chairs > self.min_chairs
        
    @property
    def is_occupied(self):
        now = timezone.now()
        # Şu anki saatten 1 saat öncesi ve sonrasını kontrol et
        time_window_start = (now - timedelta(hours=1)).time()
        time_window_end = (now + timedelta(hours=1)).time()
        
        # Eğer gece yarısını geçiyorsa özel kontrol yap
        if time_window_start > time_window_end:
            # Gece yarısını geçen durumlar için
            return self.reservations.filter(
                date=now.date(),
                time__gte=time_window_start,
                status__in=['pending', 'confirmed']
            ).exists() or self.reservations.filter(
                date=now.date() + timedelta(days=1),
                time__lte=time_window_end,
                status__in=['pending', 'confirmed']
            ).exists()
        else:
            # Normal durumlar için
            return self.reservations.filter(
                date=now.date(),
                time__gte=time_window_start,
                time__lte=time_window_end,
                status__in=['pending', 'confirmed']
            ).exists()

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('preparing', 'Hazırlanıyor'),
        ('ready', 'Hazır'),
        ('served', 'Servis Edildi'),
        ('cancelled', 'İptal Edildi'),
    ]
    
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Sipariş #{self.id} - Masa {self.table.number}"

    @property
    def total_amount(self):
        return sum(item.subtotal for item in self.order_items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"

    @property
    def subtotal(self):
        return self.quantity * self.price

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Beklemede'),
        ('confirmed', 'Onaylandı'),
        ('cancelled', 'İptal Edildi'),
        ('completed', 'Tamamlandı'),
    ]
    
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='reservations')
    number_of_guests = models.IntegerField(validators=[MinValueValidator(2), MaxValueValidator(12)])
    date = models.DateField()
    time = models.TimeField()
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.customer_name} - {self.date} {self.time}"

    def save(self, *args, **kwargs):
        if self.pk is None:  # Yeni rezervasyon
            self.table.current_chairs = self.number_of_guests
            self.table.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.table.current_chairs = self.table.min_chairs
        self.table.save()
        super().delete(*args, **kwargs)
