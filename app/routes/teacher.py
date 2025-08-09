from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models import Category, Device, Reservation
from app.forms import CategoryForm, DeviceForm
from app import db
from app.utils.decorators import login_required, teacher_required

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')

@teacher_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
@teacher_required
def dashboard():
    category_form = CategoryForm()
    device_form = DeviceForm()
    # Kategori seçim alanını (SelectField) veritabanındaki kategorilerle doldur
    device_form.category.choices = [(c.id, c.name) for c in Category.query.order_by('name').all()]

    # Kategori ekleme formu gönderildiyse
    if 'submit_category' in request.form and category_form.validate_on_submit():
        new_category = Category(name=category_form.name.data)
        db.session.add(new_category)
        db.session.commit()
        flash('Yeni kategori başarıyla eklendi!', 'success')
        return redirect(url_for('teacher.dashboard'))

    # Cihaz ekleme formu gönderildiyse
    if 'submit_device' in request.form and device_form.validate_on_submit():
        new_device = Device(name=device_form.name.data,
                              description=device_form.description.data,
                              quantity=device_form.quantity.data,
                              category_id=device_form.category.data)
        db.session.add(new_device)
        db.session.commit()
        flash('Yeni cihaz başarıyla eklendi!', 'success')
        return redirect(url_for('teacher.dashboard'))

    # Sayfayı görüntülemek için gerekli verileri çek
    categories = Category.query.order_by('name').all()
    pending_reservations = Reservation.query.filter_by(status='pending').order_by(Reservation.created_at.desc()).all()
    
    # Verileri ve formları şablona gönder
    return render_template('teacher_dashboard.html', 
                           category_form=category_form, 
                           device_form=device_form,
                           categories=categories,
                           pending_reservations=pending_reservations)

@teacher_bp.route('/approve/<int:reservation_id>')
@login_required
@teacher_required
def approve_reservation(reservation_id):
    # Rezervasyonun varlığını ve durumunu kontrol et (IDOR Koruması)
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.status != 'pending':
        flash('Bu rezervasyon isteği zaten işleme alınmış.', 'warning')
        return redirect(url_for('teacher.dashboard'))

    reservation.status = 'approved'
    db.session.commit()
    flash(f'{reservation.requester.name} kullanıcısının {reservation.device.name} için yaptığı rezervasyon isteği onaylandı.', 'success')
    return redirect(url_for('teacher.dashboard'))

@teacher_bp.route('/reject/<int:reservation_id>')
@login_required
@teacher_required
def reject_reservation(reservation_id):
    # Rezervasyonun varlığını ve durumunu kontrol et (IDOR Koruması)
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.status != 'pending':
        flash('Bu rezervasyon isteği zaten işleme alınmış.', 'warning')
        return redirect(url_for('teacher.dashboard'))
        
    reservation.status = 'rejected'
    db.session.commit()
    flash(f'{reservation.requester.name} kullanıcısının {reservation.device.name} için yaptığı rezervasyon isteği reddedildi.', 'info')
    return redirect(url_for('teacher.dashboard'))