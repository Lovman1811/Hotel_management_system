from flask import Blueprint, render_template, session
from flask_login import login_required, current_user
from database import get_db

main_bp = Blueprint('main', __name__)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    user_type = session.get('user_type', 'Staff')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM online_bookings ORDER BY registration_date DESC')
    online_bookings = cursor.fetchall()
    conn.close()
    return render_template('main/dashboard.html', user_type=user_type, online_bookings=online_bookings)

@main_bp.route('/dashboard.html')
@login_required
def dashboard_html():
    return render_template('main/dashboard.html')
