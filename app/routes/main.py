from flask import Blueprint, render_template, session
from app.utils.decorators import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def home():
    """
    Ana sayfa endpointi. Giriş yapan kullanıcıya gösterilir.
    """
    return render_template('home.html') 