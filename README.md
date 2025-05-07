# SAN Rezervasyon - Restoran Yönetim Sistemi

Bu proje, restoranlar için geliştirilmiş kapsamlı bir rezervasyon ve yönetim sistemidir. Müşterilerin masa rezervasyonu yapabilmesi, menüyü görüntüleyebilmesi ve sipariş verebilmesi için tasarlanmıştır.

## Özellikler

### Müşteriler İçin
- 🍽️ Detaylı menü görüntüleme
- 📅 Online masa rezervasyonu
- 🪑 Masa kapasitesi ve sandalye sayısı seçimi
- 🛍️ Sipariş oluşturma ve takip etme
- 📱 Responsive tasarım (mobil uyumlu)

### Yöneticiler İçin
- 👤 Kullanıcı yönetimi
- 🏪 Masa yönetimi
- 📋 Menü yönetimi
- 📊 Sipariş takibi
- 🔒 Güvenli admin paneli

## Teknik Detaylar

### Kullanılan Teknolojiler
- Python 3.x
- Django 5.2
- Bootstrap 5
- SQLite (Geliştirme)
- Crispy Forms
- Bootstrap Icons

### Proje Yapısı
```
restaurant/
├── core/                    # Ana uygulama
│   ├── migrations/         # Veritabanı migrasyonları
│   ├── static/            # Statik dosyalar (CSS, JS, resimler)
│   ├── templates/         # HTML şablonları
│   ├── admin.py          # Admin panel yapılandırması
│   ├── models.py         # Veritabanı modelleri
│   ├── views.py          # Görünüm fonksiyonları
│   └── urls.py           # URL yapılandırması
├── restaurant/            # Proje ana dizini
│   ├── settings.py       # Proje ayarları
│   ├── urls.py          # Ana URL yapılandırması
│   └── wsgi.py          # WSGI yapılandırması
├── media/                # Yüklenen medya dosyaları
├── static/              # Proje statik dosyaları
└── manage.py            # Django yönetim scripti
```

## Kurulum

1. Projeyi klonlayın:
```bash
git clone [proje-url]
cd restaurant
```

2. Sanal ortam oluşturun ve aktifleştirin:
```bash
python -m venv venv
# Windows için:
venv\Scripts\activate
# Linux/Mac için:
source venv/bin/activate
```

3. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

4. Veritabanı migrasyonlarını uygulayın:
```bash
python manage.py migrate
```

5. Süper kullanıcı oluşturun:
```bash
python manage.py createsuperuser
```

6. Geliştirme sunucusunu başlatın:
```bash
python manage.py runserver
```

## Kullanım

### Admin Paneli
- URL: `http://127.0.0.1:8000/admin`
- Oluşturduğunuz süper kullanıcı bilgileriyle giriş yapın
- Menü öğeleri, masalar ve kullanıcıları yönetin

### Müşteri Arayüzü
- Ana Sayfa: `http://127.0.0.1:8000/`
- Menü: `http://127.0.0.1:8000/menu`
- Rezervasyon: `http://127.0.0.1:8000/reservation`

## Veritabanı Modelleri

### MenuItem (Menü Öğesi)
- name: Ürün adı
- description: Ürün açıklaması
- price: Fiyat
- category: Kategori (ForeignKey)
- image: Ürün resmi
- is_available: Stok durumu

### Table (Masa)
- number: Masa numarası
- capacity: Kapasite
- min_chairs: Minimum sandalye sayısı
- max_chairs: Maksimum sandalye sayısı
- current_chairs: Mevcut sandalye sayısı
- is_occupied: Doluluk durumu

### Reservation (Rezervasyon)
- table: Masa (ForeignKey)
- customer_name: Müşteri adı
- customer_email: Müşteri e-posta
- customer_phone: Müşteri telefon
- date: Tarih
- time: Saat
- number_of_guests: Misafir sayısı
- status: Rezervasyon durumu

### Order (Sipariş)
- table: Masa (ForeignKey)
- status: Sipariş durumu
- created_at: Oluşturulma tarihi
- updated_at: Güncellenme tarihi

## Güvenlik

- Django'nun güvenlik özellikleri aktif
- CSRF koruması
- XSS koruması
- SQL injection koruması
- Güvenli şifreleme

## Geliştirme

### Yeni Özellik Ekleme
1. Yeni bir branch oluşturun
2. Değişikliklerinizi yapın
3. Testleri çalıştırın
4. Pull request oluşturun

### Test Etme
```bash
python manage.py test
```

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## İletişim

Proje Sahibi: İbrahim Buğra San
E-posta: ibugrasan@gmail.com
GitHub: https://github.com/ibrahimbugrasan

## Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

---

# English

# SAN Reservation - Restaurant Management System

This project is a comprehensive reservation and management system developed for restaurants. It is designed to allow customers to make table reservations, view menus, and place orders.

## Features

### For Customers
- 🍽️ Detailed menu viewing
- 📅 Online table reservation
- 🪑 Table capacity and chair count selection
- 🛍️ Order creation and tracking
- 📱 Responsive design (mobile-friendly)

### For Administrators
- 👤 User management
- 🏪 Table management
- 📋 Menu management
- 📊 Order tracking
- 🔒 Secure admin panel

## Technical Details

### Technologies Used
- Python 3.x
- Django 5.2
- Bootstrap 5
- SQLite (Development)
- Crispy Forms
- Bootstrap Icons

### Project Structure
```
restaurant/
├── core/                    # Main application
│   ├── migrations/         # Database migrations
│   ├── static/            # Static files (CSS, JS, images)
│   ├── templates/         # HTML templates
│   ├── admin.py          # Admin panel configuration
│   ├── models.py         # Database models
│   ├── views.py          # View functions
│   └── urls.py           # URL configuration
├── restaurant/            # Project root directory
│   ├── settings.py       # Project settings
│   ├── urls.py          # Main URL configuration
│   └── wsgi.py          # WSGI configuration
├── media/                # Uploaded media files
├── static/              # Project static files
└── manage.py            # Django management script
```

## Installation

1. Clone the project:
```bash
git clone [project-url]
cd restaurant
```

2. Create and activate virtual environment:
```bash
python -m venv venv
# For Windows:
venv\Scripts\activate
# For Linux/Mac:
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Apply database migrations:
```bash
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Start development server:
```bash
python manage.py runserver
```

## Usage

### Admin Panel
- URL: `http://127.0.0.1:8000/admin`
- Login with your superuser credentials
- Manage menu items, tables, and users

### Customer Interface
- Home Page: `http://127.0.0.1:8000/`
- Menu: `http://127.0.0.1:8000/menu`
- Reservation: `http://127.0.0.1:8000/reservation`

## Database Models

### MenuItem
- name: Product name
- description: Product description
- price: Price
- category: Category (ForeignKey)
- image: Product image
- is_available: Stock status

### Table
- number: Table number
- capacity: Capacity
- min_chairs: Minimum chair count
- max_chairs: Maximum chair count
- current_chairs: Current chair count
- is_occupied: Occupancy status

### Reservation
- table: Table (ForeignKey)
- customer_name: Customer name
- customer_email: Customer email
- customer_phone: Customer phone
- date: Date
- time: Time
- number_of_guests: Number of guests
- status: Reservation status

### Order
- table: Table (ForeignKey)
- status: Order status
- created_at: Creation date
- updated_at: Update date

## Security

- Django security features enabled
- CSRF protection
- XSS protection
- SQL injection protection
- Secure encryption

## Development

### Adding New Features
1. Create a new branch
2. Make your changes
3. Run tests
4. Create a pull request

### Testing
```bash
python manage.py test
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

Project Owner: İbrahim Buğra San
Email: ibugrasan@gmail.com
GitHub: https://github.com/ibrahimbugrasan

## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request 