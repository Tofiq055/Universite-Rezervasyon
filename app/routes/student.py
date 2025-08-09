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
    Öğrenci panelini gösterir. Cihazları ve öğrencinin kendi rezervasyonlarını listeler.
    """
    categories = Category.query.order_by(Category.name).all()
    # Giriş yapmış öğrencinin ID'sini kullanarak kendi rezervasyonlarını çek
    user_id = session['user_id']
    my_reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.created_at.desc()).all()
    
    # Verileri ve öğrencinin rezervasyonlarını şablona gönder
    return render_template('student_dashboard.html', categories=categories, my_reservations=my_reservations)

@student_bp.route('/device/<int:device_id>', methods=['GET', 'POST'])
@login_required
@student_required
def device_detail(device_id):
    device = Device.query.get_or_404(device_id)

    # Form gönderildiğinde çalışan POST kısmı aynı kalabilir, çünkü zaten
    # 'pending' ve 'approved' durumlarını kontrol ederek doğru çalışıyor.
    if request.method == 'POST':
        # ... Bu bölümdeki kodlarda değişiklik yok ...
        reservation_date_str = request.form.get('reservation_date')
        if not reservation_date_str:
            flash('Lütfen geçerli bir tarih seçin.', 'warning')
            return redirect(url_for('student.device_detail', device_id=device.id))
        user_id = session['user_id']
        reservation_date = date.fromisoformat(reservation_date_str)
        existing_request = Reservation.query.filter_by(user_id=user_id, device_id=device.id, reservation_date=reservation_date).first()
        if existing_request:
            flash(f'Bu cihaz için {reservation_date.strftime("%d-%m-%Y")} tarihinde zaten bir rezervasyon isteğiniz mevcut.', 'warning')
            return redirect(url_for('student.device_detail', device_id=device.id))
        active_reservations_count = Reservation.query.filter(
            Reservation.device_id == device.id,
            Reservation.reservation_date == reservation_date,
            Reservation.status.in_(['approved', 'pending'])
        ).count()
        if active_reservations_count >= device.quantity:
            flash('Seçtiğiniz tarih için bu cihazın tüm stokları rezerve edilmiş veya beklemede.', 'danger')
            return redirect(url_for('student.device_detail', device_id=device.id))
        new_reservation = Reservation(
            user_id=user_id,
            device_id=device.id,
            reservation_date=reservation_date,
            status='pending'
        )
        db.session.add(new_reservation)
        db.session.commit()
        flash(f'{device.name} için {reservation_date.strftime("%d-%m-%Y")} tarihli rezervasyon isteğiniz başarıyla alındı.', 'success')
        return redirect(url_for('student.dashboard'))
    # --- DEĞİŞİKLİK BU KISIMDA ---
    # Takvim için müsaitlik durumunu hesapla
    today = date.today()
    availability = {}
    for i in range(30):
        current_date = today + timedelta(days=i)
        
        # Onaylanmış rezervasyonları say
        approved_count = Reservation.query.filter_by(
            device_id=device.id,
            reservation_date=current_date,
            status='approved'
        ).count()

        # Beklemedeki rezervasyonları say
        pending_count = Reservation.query.filter_by(
            device_id=device.id,
            reservation_date=current_date,
            status='pending'
        ).count()

        # Yeni duruma göre etiket belirle
        if approved_count >= device.quantity:
            availability[current_date] = 'Dolu'
        elif approved_count + pending_count >= device.quantity:
            availability[current_date] = 'Onay Bekliyor' # Yeni durum etiketi
        else:
            availability[current_date] = 'Müsait'

    return render_template('device_detail.html', device=device, availability=availability)


@student_bp.route('/my_reservations')
@login_required
@student_required
def my_reservations():
    """Giriş yapmış öğrencinin tüm rezervasyonlarını listeler."""
    user_id = session['user_id']
    reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.reservation_date.desc()).all()
    return render_template('my_reservations_student.html', reservations=reservations)