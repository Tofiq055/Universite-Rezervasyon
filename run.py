from app import create_app, db
from app.models import User, Category, Device, Reservation
import click

# Uygulamayı oluştur
app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Category': Category, 'Device': Device}

# --- KULLANICI YÖNETİMİ ---
@app.cli.command("add-user")
@click.argument("identifier")
@click.argument("password")
@click.argument("name")
@click.option("--role", default="student", help="Kullanıcı rolü (student veya teacher)")
def add_user(identifier, password, name, role):
    # ... (Bu fonksiyonun içeriği aynı kalacak)
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


# --- KATEGORİ YÖNETİMİ ---
@app.cli.command("add-category")
@click.argument("name")
def add_category(name):
    # ... (Bu fonksiyonun içeriği aynı kalacak)
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
    # ... (Bu fonksiyonun içeriği aynı kalacak)
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
    # ... (Bu fonksiyonun içeriği aynı kalacak)
    categories = Category.query.order_by('name').all()
    if not categories:
        print("Veritabanında hiç kategori bulunmuyor.")
        return
    print("--- Mevcut Kategoriler ---")
    for cat in categories:
        print(f"- {cat.name} ({cat.devices.count()} cihaz)")
    print("-------------------------")


# --- CİHAZ YÖNETİMİ ---
@app.cli.command("add-device")
@click.argument("name")
@click.argument("category_name")
@click.option("--quantity", default=1, help="Cihazın stok adedi")
@click.option("--description", default="Cihaz açıklaması mevcut değil.", help="Cihaz açıklaması")
def add_device(name, category_name, quantity, description):
    # ... (Bu fonksiyonun içeriği aynı kalacak)
    category = Category.query.filter_by(name=category_name).first()
    if not category:
        print(f"Hata: '{category_name}' adında bir kategori bulunamadı.")
        return
    device = Device(name=name, description=description, quantity=quantity, category_id=category.id)
    db.session.add(device)
    db.session.commit()
    print(f"Cihaz eklendi: '{name}' -> '{category_name}'")


# --- GÜNCELLENMİŞ CİHAZ SİLME KOMUTU ---
@app.cli.command("delete-device")
@click.argument("name")
@click.option('--force', is_flag=True, help="Cihazın mevcut rezervasyonları olsa bile silmeye zorlar.")
def delete_device(name, force):
    """Veritabanından bir cihazı siler."""
    device = Device.query.filter_by(name=name).first()
    if not device:
        print(f"Hata: '{name}' adında bir cihaz bulunamadı.")
        return

    # Eğer --force bayrağı kullanıldıysa, tüm ilişkili rezervasyonları sil
    if force:
        # Cihaza ait tüm rezervasyonları bul ve sil
        reservations_to_delete = device.reservations.all()
        num_reservations = len(reservations_to_delete)
        for res in reservations_to_delete:
            db.session.delete(res)
        
        # Cihazı sil
        db.session.delete(device)
        db.session.commit()
        print(f"Zorla Silme: '{name}' cihazı ve ilişkili {num_reservations} adet rezervasyon başarıyla silindi.")
    
    # --force bayrağı kullanılmadıysa, eski güvenli kontrolü yap
    else:
        if device.reservations.count() > 0:
            print(f"Hata: '{name}' cihazı silinemedi çünkü mevcut rezervasyonları var.")
            print("Bu cihazı ve tüm rezervasyonlarını silmek için 'flask delete-device \"{name}\" --force' komutunu kullanın.")
            return

        db.session.delete(device)
        db.session.commit()
        print(f"Cihaz silindi: '{name}'")


@app.cli.command("list-devices")
def list_devices():
    # ... (Bu fonksiyonun içeriği aynı kalacak)
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