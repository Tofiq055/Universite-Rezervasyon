from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from app.models import Category, Device, Reservation
from app import db
from app.utils.decorators import login_required, student_required
from datetime import date, timedelta

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    """
    Öğrenci panelini gösterir. Tüm kategorileri ve içlerindeki cihazları listeler.
    """
    categories = Category.query.order_by(Category.name).all()
    return render_template('student_dashboard.html', categories=categories)

@student_bp.route('/device/<int:device_id>', methods=['GET', 'POST'])
@login_required
@student_required
def device_detail(device_id):
    """
    Tek bir cihazın detaylarını, rezervasyon takvimini gösterir ve rezervasyon isteği alır.
    """
    device = Device.query.get_or_404(device_id)

    if request.method == 'POST':
        reservation_date_str = request.form.get('reservation_date')
        if not reservation_date_str:
            flash('Lütfen geçerli bir tarih seçin.', 'warning')
            return redirect(url_for('student.device_detail', device_id=device.id))

        user_id = session['user_id']
        reservation_date = date.fromisoformat(reservation_date_str)

        # Güvenlik Kontrolü: Kullanıcının o gün için zaten bir isteği var mı?
        existing_request = Reservation.query.filter_by(user_id=user_id, device_id=device.id, reservation_date=reservation_date).first()
        if existing_request:
            flash(f'Bu cihaz için {reservation_date.strftime("%d-%m-%Y")} tarihinde zaten bir rezervasyon isteğiniz mevcut.', 'warning')
            return redirect(url_for('student.device_detail', device_id=device.id))

        # Stok Kontrolü: O günkü onaylı rezervasyonlar stokta yer bırakıyor mu?
        approved_reservations_count = Reservation.query.filter_by(
            device_id=device.id,
            reservation_date=reservation_date,
            status='approved'
        ).count()

        if approved_reservations_count >= device.quantity:
            flash('Seçtiğiniz tarih için bu cihazın tüm stokları rezerve edilmiş durumda.', 'danger')
            return redirect(url_for('student.device_detail', device_id=device.id))
            
        # Yeni rezervasyon isteğini veritabanına ekle
        new_reservation = Reservation(
            user_id=user_id,
            device_id=device.id,
            reservation_date=reservation_date,
            status='pending' # İstek 'beklemede' durumuyla başlar
        )
        db.session.add(new_reservation)
        db.session.commit()
        flash(f'{device.name} için {reservation_date.strftime("%d-%m-%Y")} tarihli rezervasyon isteğiniz başarıyla alındı. Öğretmen onayı bekleniyor.', 'success')
        # İstek sonrası ana panele yönlendir
        return redirect(url_for('student.dashboard'))

    # Takvim için müsaitlik durumunu hesapla
    today = date.today()
    availability = {}
    for i in range(30): # Önümüzdeki 30 günün takvimini oluştur
        current_date = today + timedelta(days=i)
        approved_count = Reservation.query.filter_by(
            device_id=device.id,
            reservation_date=current_date,
            status='approved'
        ).count()
        
        if approved_count >= device.quantity:
            availability[current_date] = 'Dolu'
        else:
            availability[current_date] = 'Müsait'

    return render_template('device_detail.html', device=device, availability=availability)