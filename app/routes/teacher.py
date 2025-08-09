from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models import Category, Device, Reservation
from app.forms import CategoryForm, DeviceForm
from app import db
from app.utils.decorators import login_required, teacher_required
from collections import defaultdict # Gruplama için bu modülü ekliyoruz

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')

# --- ANA DASHBOARD (BEKLEYEN İSTEKLER) ---
@teacher_bp.route('/dashboard')
@login_required
@teacher_required
def dashboard():
    """Öğretmenin ana paneli, bekleyen istekleri kategorilere göre gruplanmış gösterir."""
    
    # Bekleyen tüm rezervasyonları çekiyoruz
    pending_reservations = Reservation.query.filter_by(status='pending').order_by(Reservation.created_at.desc()).all()
    
    # --- YENİ GRUPLAMA MANTIĞI BURADA ---
    # Rezervasyonları kategorilerine göre gruplamak için bir sözlük (dictionary) oluşturuyoruz
    requests_by_category = defaultdict(list)
    for res in pending_reservations:
        # Her rezervasyonu kendi kategorisinin listesine ekliyoruz
        requests_by_category[res.device.category].append(res)
    
    # Şablona artık basit ve gruplanmış veriyi gönderiyoruz
    return render_template('teacher_dashboard.html', requests_by_category=requests_by_category)


# --- ENVANTER YÖNETİMİ (YENİ SAYFA) ---
@teacher_bp.route('/inventory')
@login_required
@teacher_required
def manage_inventory():
    """Tüm kategorileri ve cihazları listeleyen yönetim sayfası."""
    categories = Category.query.order_by(Category.name).all()
    devices = Device.query.order_by(Device.name).all()
    return render_template('manage_inventory.html', categories=categories, devices=devices)


# --- KATEGORİ EKLE/DÜZENLE ---
# ... (add_category ve edit_category fonksiyonları aynı kalacak) ...
@teacher_bp.route('/category/add', methods=['GET', 'POST'])
@login_required
@teacher_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        new_category = Category(name=form.name.data)
        db.session.add(new_category)
        db.session.commit()
        flash('Kategori başarıyla eklendi.', 'success')
        return redirect(url_for('teacher.manage_inventory'))
    return render_template('form_page.html', title='Yeni Kategori Ekle', form=form)

@teacher_bp.route('/category/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('Kategori başarıyla güncellendi.', 'success')
        return redirect(url_for('teacher.manage_inventory'))
    return render_template('form_page.html', title='Kategoriyi Düzenle', form=form)


# --- CİHAZ EKLE/DÜZENLE ---
# ... (add_device ve edit_device fonksiyonları aynı kalacak) ...
@teacher_bp.route('/device/add', methods=['GET', 'POST'])
@login_required
@teacher_required
def add_device():
    form = DeviceForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.order_by('name').all()]
    if form.validate_on_submit():
        new_device = Device(name=form.name.data,
                              description=form.description.data,
                              quantity=form.quantity.data,
                              category_id=form.category.data)
        db.session.add(new_device)
        db.session.commit()
        flash('Cihaz başarıyla eklendi.', 'success')
        return redirect(url_for('teacher.manage_inventory'))
    return render_template('form_page.html', title='Yeni Cihaz Ekle', form=form)

@teacher_bp.route('/device/edit/<int:device_id>', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_device(device_id):
    device = Device.query.get_or_404(device_id)
    form = DeviceForm(obj=device)
    form.category.choices = [(c.id, c.name) for c in Category.query.order_by('name').all()]
    if form.validate_on_submit():
        device.name = form.name.data
        device.description = form.description.data
        device.quantity = form.quantity.data
        device.category_id = form.category.data
        db.session.commit()
        flash('Cihaz başarıyla güncellendi.', 'success')
        return redirect(url_for('teacher.manage_inventory'))
    return render_template('form_page.html', title='Cihazı Düzenle', form=form)


# --- SİLME İŞLEMLERİ ---
# ... (delete_item fonksiyonu aynı kalacak) ...
@teacher_bp.route('/delete/<item_type>/<int:item_id>', methods=['GET', 'POST'])
@login_required
@teacher_required
def delete_item(item_type, item_id):
    if item_type == 'category':
        item = Category.query.get_or_404(item_id)
        if item.devices.count() > 0:
            flash('Bu kategoriyi silemezsiniz çünkü içinde cihazlar var. Önce cihazları silin.', 'danger')
            return redirect(url_for('teacher.manage_inventory'))
    elif item_type == 'device':
        item = Device.query.get_or_404(item_id)
        if item.reservations.count() > 0:
            flash('Bu cihazı silemezsiniz çünkü rezervasyon geçmişi var. Cihazı silmek için veritabanından manuel işlem gerekir.', 'danger')
            return redirect(url_for('teacher.manage_inventory'))
    else:
        return redirect(url_for('teacher.dashboard'))

    if request.method == 'POST':
        db.session.delete(item)
        db.session.commit()
        flash(f'{item_type.capitalize()} başarıyla silindi.', 'success')
        return redirect(url_for('teacher.manage_inventory'))
    return render_template('delete_confirmation.html', item_name=item.name, item_type=item_type)


# --- BİREYSEL VE TOPLU REZERVASYON İŞLEMLERİ ---
# ... (approve_reservation, reject_reservation, approve_category, reject_category fonksiyonları aynı kalacak) ...
@teacher_bp.route('/approve/<int:reservation_id>')
@login_required
@teacher_required
def approve_reservation(reservation_id):
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
    reservation = Reservation.query.get_or_404(reservation_id)
    if reservation.status != 'pending':
        flash('Bu rezervasyon isteği zaten işleme alınmış.', 'warning')
        return redirect(url_for('teacher.dashboard'))
    reservation.status = 'rejected'
    db.session.commit()
    flash(f'{reservation.requester.name} kullanıcısının {reservation.device.name} için yaptığı rezervasyon isteği reddedildi.', 'info')
    return redirect(url_for('teacher.dashboard'))

@teacher_bp.route('/approve/category/<int:category_id>')
@login_required
@teacher_required
def approve_category(category_id):
    reservations_to_approve = Reservation.query.join(Device).filter(
        Device.category_id == category_id,
        Reservation.status == 'pending'
    ).all()
    if not reservations_to_approve:
        flash('Bu kategoride onaylanacak bekleyen istek bulunmuyor.', 'info')
        return redirect(url_for('teacher.dashboard'))
    approved_count = 0
    for res in reservations_to_approve:
        approved_on_date = Reservation.query.filter_by(
            device_id=res.device_id,
            reservation_date=res.reservation_date,
            status='approved'
        ).count()
        if approved_on_date < res.device.quantity:
            res.status = 'approved'
            approved_count += 1
    db.session.commit()
    flash(f'{approved_count} adet rezervasyon isteği başarıyla onaylandı. Stok yetersizliği nedeniyle bazıları onaylanmamış olabilir.', 'success')
    return redirect(url_for('teacher.dashboard'))

@teacher_bp.route('/reject/category/<int:category_id>')
@login_required
@teacher_required
def reject_category(category_id):
    reservations_to_reject = Reservation.query.join(Device).filter(
        Device.category_id == category_id,
        Reservation.status == 'pending'
    ).all()
    if not reservations_to_reject:
        flash('Bu kategoride reddedilecek bekleyen istek bulunmuyor.', 'info')
        return redirect(url_for('teacher.dashboard'))
    rejected_count = len(reservations_to_reject)
    for res in reservations_to_reject:
        res.status = 'rejected'
    db.session.commit()
    flash(f'{rejected_count} adet rezervasyon isteği başarıyla reddedildi.', 'info')
    return redirect(url_for('teacher.dashboard'))

@teacher_bp.route('/approved_reservations')
@login_required
@teacher_required
def approved_reservations():
    """Onaylanmış tüm rezervasyonları listeler."""
    reservations = Reservation.query.filter_by(status='approved').order_by(Reservation.reservation_date.desc()).all()
    return render_template('approved_reservations_teacher.html', reservations=reservations)