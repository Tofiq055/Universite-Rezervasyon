from flask import Blueprint

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """
    Ana sayfa endpointi.
    """
    return 'Hello, Reservation System!' 