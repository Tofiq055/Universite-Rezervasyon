# Reservation System

Basit bir Flask tabanlı rezervasyon sistemi iskeleti.

## Özellikler
- Flask app factory yapısı
- Blueprint ile route yönetimi
- Geliştirilebilir model ve config altyapısı

## Proje Yapısı
```
project_root/
│
├── app/
│   ├── __init__.py
│   ├── routes/
│   │   └── main.py
│   └── models/
│       └── __init__.py
├── config.py
├── run.py
├── requirements.txt
└── README.md
```

## Kurulum
1. Depoyu klonlayın:
   ```bash
   git clone https://github.com/Tofiq055/Universite-Rezervasyon
   cd reservation
   ```
2. Sanal ortam oluşturun ve aktif edin (isteğe bağlı):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. Gereksinimleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

## Çalıştırma
```bash
python run.py
```
Tarayıcıda [http://localhost:5000](http://localhost:5000) adresine gidin.

## Katkı
Katkıda bulunmak için lütfen bir pull request açın veya issue oluşturun.

## Lisans
Bu proje MIT lisansı ile lisanslanmıştır.
