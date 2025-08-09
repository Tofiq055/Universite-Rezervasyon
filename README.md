
# Üniversite Laboratuvar Rezervasyon Sistemi

Python ve Flask tabanlı, öğrenci ve öğretmen rolleri için tasarlanmış bir laboratuvar cihazı rezervasyon sistemi.

## Özellikler
- **Kullanıcı Rolleri:** Öğrenci ve Öğretmen olarak iki farklı yetki seviyesi.
- **Envanter Yönetimi:** Öğretmenler için web arayüzünden Kategori ve Cihaz ekleme, düzenleme ve silme (CRUD) işlemleri.
- **Rezervasyon Döngüsü:** Öğrenciler için tarih bazlı rezervasyon isteği gönderme ve kendi rezervasyonlarının durumunu (Beklemede, Onaylandı, Reddedildi) takip etme.
- **Öğretmen Paneli:** Bekleyen rezervasyon isteklerini görüntüleme, bireysel veya kategori bazında toplu onay/red işlemleri yapma.
- **Komut Satırı Arayüzü:** Veritabanını yönetmek için `flask` komutları (kullanıcı/cihaz ekleme, listeleme, silme vb.).

## Kurulum

Projeyi yerel makinenizde sıfırdan kurup çalıştırmak için aşağıdaki adımları izleyin.

**1. Depoyu Klonlayın:**
```bash
git clone https://github.com/Tofiq055/Universite-Rezervasyon
cd Universite-Rezervasyon
````

**2. Sanal Ortam Oluşturun ve Aktif Edin:**
Sanal ortam, proje bağımlılıklarını sisteminizden izole ederek çakışmaları önler.

```bash
# Sanal ortamı oluştur
python -m venv venv

# Sanal ortamı aktif et
# Windows:
venv\Scripts\activate
# macOS / Linux:
# source venv/bin/activate
```

**3. Gerekli Paketleri Yükleyin:**
Projenin ihtiyaç duyduğu tüm kütüphaneleri `requirements.txt` dosyasından yükleyin.

```bash
pip install -r requirements.txt
```

**4. Ortam Değişkenleri Dosyasını Oluşturun:**
Projenin çalışması için gerekli olan `FLASK_APP` değişkenini ayarlayın. `.flaskenv.example` dosyasını kopyalayarak `.flaskenv` adında yeni bir dosya oluşturun.

```bash
# Windows:
copy .flaskenv.example .flaskenv
# macOS / Linux:
# cp .flaskenv.example .flaskenv
```

Bu dosyanın içinde `FLASK_APP=run.py` yazdığından emin olun.

**5. Veritabanını Oluşturun:**
Boş veritabanı dosyasını ve tabloları oluşturmak için aşağıdaki `flask db` komutunu çalıştırın:

```bash
flask db upgrade
```

Bu komut, proje ana dizininde `db.sqlite3` adında bir veritabanı dosyası oluşturacaktır.

**6. İlk Kullanıcıları Oluşturun (Önerilir):**
Uygulamayı test etmek için bir öğretmen ve bir öğrenci hesabı oluşturun.

```bash
# Örnek Öğretmen Hesabı
flask add-user "P1001" "ogretmen123" "Prof. Dr. Ali Veli" --role teacher

# Örnek Öğrenci Hesabı
flask add-user "20250101" "ogrenci123" "Zeynep Yılmaz" --role student
```

## Çalıştırma

Kurulum tamamlandıktan sonra, Flask geliştirme sunucusunu başlatmak için aşağıdaki komutu kullanın:

```bash
flask run
```

Uygulama varsayılan olarak [http://127.0.0.1:5000](https://www.google.com/search?q=http://127.0.0.1:5000) adresinde çalışacaktır.

## Komut Satırı Yönetimi

Uygulama, `flask` komutları aracılığıyla veritabanını yönetmek için çeşitli araçlar sunar:

  - `flask list-categories`: Tüm kategorileri listeler.
  - `flask list-devices`: Tüm cihazları listeler.
  - `flask add-category "Kategori Adı"`: Yeni kategori ekler.
  - `flask add-device "Cihaz Adı" "Kategori Adı" --quantity 5`: Yeni cihaz ekler.
  - `flask delete-device "Cihaz Adı" --force`: Cihazı ve tüm ilişkili rezervasyonlarını siler.

<!-- end list -->

```
```
