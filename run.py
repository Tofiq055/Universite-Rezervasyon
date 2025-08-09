from app import create_app, db
from app.models import User, Category, Device, Reservation
import click

# Uygulamayı oluştur
app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Flask shell için veritabanı nesnelerini ve modelleri otomatik olarak import eder."""
    return {'db': db, 'User': User, 'Category': Category, 'Device': Device, 'Reservation': Reservation}

# --- VERİTABANI YÖNETİM KOMUTLARI ---

@app.cli.command("seed-db")
def seed_db():
    """Veritabanını başlangıçtaki örnek verilerle doldurur."""
    if Category.query.first():
        print("Veritabanı zaten başlangıç verilerini içeriyor. İşlem atlandı.")
        return

    print("Veritabanına başlangıç verileri ekleniyor...")

    seed_data = {
        "Mikroskoplar": [
            {"name": "Olympus CX23 Işık Mikroskobu", "quantity": 3, "description": "Eğitim ve rutin laboratuvar çalışmaları için ideal, LED aydınlatmalı binoküler mikroskop."},
            {"name": "Leica DMi8 Floresan Mikroskobu", "quantity": 1, "description": "Gelişmiş hücre görüntüleme ve canlı hücre analizi için ters tip floresan mikroskop."}
        ],
        "Spektrometreler": [
            {"name": "Thermo Scientific NanoDrop One", "quantity": 2, "description": "DNA, RNA ve protein miktarını ölçmek için kullanılan mikro-hacim UV-Vis spektrofotometre."},
            {"name": "Agilent Cary 630 FTIR", "quantity": 1, "description": "Kimyasal bağ analizi için kullanılan, taşınabilir ve sağlam Fourier Dönüşümlü Kızılötesi Spektrometresi."}
        ],
        "Santrifüjler": [
            {"name": "Eppendorf 5424 R Soğutmalı Mikro Santrifüj", "quantity": 5, "description": "24 tüp kapasiteli, 21,130 x g'ye kadar hız yapabilen soğutmalı mikro santrifüj."},
            {"name": "Beckman Coulter Avanti J-26S XP", "quantity": 1, "description": "Büyük hacimli örneklerin ayrıştırılması için kullanılan yüksek performanslı santrifüj."}
        ],
        "Genel Ekipmanlar": [
            {"name": "Heidolph Hei-PLATE Manyetik Karıştırıcı", "quantity": 10, "description": "Isıtma ve karıştırma işlemleri için hassas kontrollü laboratuvar ekipmanı."},
            {"name": "Mettler Toledo ME204 Analitik Terazi", "quantity": 4, "description": "0.1 mg hassasiyetle ölçüm yapabilen, yüksek doğrulukta analitik terazi."}
        ]
    }

    for category_name, devices in seed_data.items():
        new_category = Category(name=category_name)
        db.session.add(new_category)
        
        for device_info in devices:
            new_device = Device(
                name=device_info["name"],
                quantity=device_info["quantity"],
                description=device_info["description"],
                category=new_category
            )
            db.session.add(new_device)
            
    db.session.commit()
    print("Veritabanı başarıyla dolduruldu!")

@app.cli.command("add-user")
@click.argument("identifier")
@click.argument("password")
@click.argument("name")
@click.option("--role", default="student", help="Kullanıcı rolü (student veya teacher)")
def add_user(identifier, password, name, role):
    """Veritabanına yeni bir kullanıcı ekler."""
    if role not in ['student', 'teacher']:
        print("Hata: Rol 'student' veya 'teacher' olmalıdır.")
        return
    if User.query.filter_by(identifier=identifier).first():
        print(f"Hata: '{identifier}' numaralı kullanıcı zaten mevcut.")
        return
    user = User(identifier=identifier, name=name, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print(f"'{name}' isimli, '{role}' rolündeki kullanıcı başarıyla eklendi.")

@app.cli.command("add-category")
@click.argument("name")
def add_category(name):
    """Veritabanına yeni bir cihaz kategorisi ekler."""
    if Category.query.filter_by(name=name).first():
        print(f"Hata: '{name}' adında bir kategori zaten mevcut.")
        return
    category = Category(name=name)
    db.session.add(category)
    db.session.commit()
    print(f"Kategori eklendi: '{name}'")

@app.cli.command("delete-category")
@click.argument("name")
def delete_category(name):
    """Veritabanından bir kategoriyi siler."""
    category = Category.query.filter_by(name=name).first()
    if not category:
        print(f"Hata: '{name}' adında bir kategori bulunamadı.")
        return
    if category.devices.count() > 0:
        print(f"Hata: '{name}' kategorisi silinemedi çünkü içinde cihazlar var. Lütfen önce bu kategorideki cihazları silin.")
        return
    db.session.delete(category)
    db.session.commit()
    print(f"Kategori silindi: '{name}'")

@app.cli.command("list-categories")
def list_categories():
    """Veritabanındaki tüm kategorileri listeler."""
    categories = Category.query.order_by('name').all()
    if not categories:
        print("Veritabanında hiç kategori bulunmuyor.")
        return
    print("--- Mevcut Kategoriler ---")
    for cat in categories:
        print(f"- {cat.name} ({cat.devices.count()} cihaz)")
    print("-------------------------")

@app.cli.command("add-device")
@click.argument("name")
@click.argument("category_name")
@click.option("--quantity", default=1, help="Cihazın stok adedi")
@click.option("--description", default="Cihaz açıklaması mevcut değil.", help="Cihaz açıklaması")
def add_device(name, category_name, quantity, description):
    """Veritabanına yeni bir cihaz ekler."""
    category = Category.query.filter_by(name=category_name).first()
    if not category:
        print(f"Hata: '{category_name}' adında bir kategori bulunamadı.")
        return
    device = Device(name=name, description=description, quantity=quantity, category_id=category.id)
    db.session.add(device)
    db.session.commit()
    print(f"Cihaz eklendi: '{name}' -> '{category_name}'")

@app.cli.command("delete-device")
@click.argument("name")
@click.option('--force', is_flag=True, help="Cihazın mevcut rezervasyonları olsa bile silmeye zorlar.")
def delete_device(name, force):
    """Veritabanından bir cihazı siler."""
    device = Device.query.filter_by(name=name).first()
    if not device:
        print(f"Hata: '{name}' adında bir cihaz bulunamadı.")
        return

    if force:
        reservations_to_delete = device.reservations.all()
        num_reservations = len(reservations_to_delete)
        for res in reservations_to_delete:
            db.session.delete(res)
        
        db.session.delete(device)
        db.session.commit()
        print(f"Zorla Silme: '{name}' cihazı ve ilişkili {num_reservations} adet rezervasyon başarıyla silindi.")
    else:
        if device.reservations.count() > 0:
            print(f"Hata: '{name}' cihazı silinemedi çünkü mevcut rezervasyonları var.")
            print(f"Bu cihazı ve tüm rezervasyonlarını silmek için 'flask delete-device \"{name}\" --force' komutunu kullanın.")
            return

        db.session.delete(device)
        db.session.commit()
        print(f"Cihaz silindi: '{name}'")

@app.cli.command("list-devices")
def list_devices():
    """Veritabanındaki tüm cihazları kategorilere göre listeler."""
    categories = Category.query.order_by('name').all()
    if not categories:
        print("Veritabanında hiç cihaz veya kategori bulunmuyor.")
        return
    print("--- Mevcut Cihazlar ---")
    for cat in categories:
        print(f"\nKategori: {cat.name}")
        if not cat.devices.all():
            print("  Bu kategoride cihaz yok.")
        else:
            for dev in cat.devices:
                print(f"  - {dev.name} (Stok: {dev.quantity})")
    print("\n------------------------")

if __name__ == '__main__':
    app.run()
