from flask import Blueprint, jsonify
from flask_login import login_required
from database import get_db

api_bp = Blueprint('api', __name__)


@api_bp.route('/dashboard-stats')
@login_required
def dashboard_stats():
    conn = get_db()
    cursor = conn.cursor()

    # Get total guests
    cursor.execute('SELECT COUNT(*) FROM guest')
    total_guests = cursor.fetchone()[0]

    # Get total bookings
    cursor.execute('SELECT COUNT(*) FROM room_book')
    total_bookings = cursor.fetchone()[0]

    # Get total staff
    cursor.execute('SELECT COUNT(*) FROM staff_detail')
    total_staff = cursor.fetchone()[0]

    # Get available rooms (total rooms - booked rooms)
    cursor.execute('SELECT COUNT(*) FROM floors_rooms')
    total_rooms = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(DISTINCT room) FROM room_book')
    booked_rooms = cursor.fetchone()[0]

    available_rooms = total_rooms - booked_rooms

    conn.close()

    return jsonify({
        'guests': total_guests,
        'bookings': total_bookings,
        'staff': total_staff,
        'rooms': available_rooms
    })
