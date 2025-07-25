from app import create_app, db
from app.models import User
import click # Flask ile gelen bir kütüphane, komut satırı arayüzü için

# Uygulamayı oluştur
app = create_app()

# Bu 'with' bloğu, veritabanı komutlarının uygulama bağlamında çalışmasını sağlar
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

# Yeni kullanıcı eklemek için özel bir komut oluşturuyoruz
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
        
    # Kullanıcının zaten var olup olmadığını kontrol et
    if User.query.filter_by(identifier=identifier).first():
        print(f"Hata: '{identifier}' numaralı kullanıcı zaten mevcut.")
        return
        
    user = User(identifier=identifier, name=name, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print(f"'{name}' isimli, '{role}' rolündeki kullanıcı başarıyla eklendi.")


if __name__ == '__main__':
    app.run()