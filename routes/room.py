from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from database import get_db

room_bp = Blueprint('room', __name__)


@room_bp.route('/booking')
@login_required
def booking():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM room_book ORDER BY id DESC')
    bookings = cursor.fetchall()

    # Fetch housekeeping status for rooms
    cursor.execute('SELECT floor, room_number, status FROM housekeeping')
    housekeeping_status = cursor.fetchall()
    status_map = {}
    for row in housekeeping_status:
        key = (row['floor'], row['room_number'])
        status_map[key] = row['status']

    # Add status to bookings
    bookings_with_status = []
    for booking in bookings:
        key = (booking['floor'], booking['room'])
        status = status_map.get(key, 'Unknown')
        booking_dict = dict(booking)
        booking_dict['status'] = status
        bookings_with_status.append(booking_dict)

    try:
        cursor.execute('SELECT DISTINCT floor FROM housekeeping')
        floors = [row['floor'] for row in cursor.fetchall()]
    except Exception as e:
        floors = []
        flash(f'Error fetching floors: {str(e)}', 'error')
    finally:
        conn.close()
    return render_template('room/booking.html', bookings=bookings_with_status, floors=floors)


@room_bp.route('/add-booking', methods=['POST'])
@login_required
def add_booking():
    try:
        data = (
            request.form['contact'],
            request.form['room_type'],
            request.form['floor'],
            request.form['room'],
            request.form['check_in'],
            request.form['check_out']
        )

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO room_book (contact, room_type, floor, room, check_in, check_out)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', data)
        conn.commit()
        conn.close()

        flash('Booking added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding booking: {str(e)}', 'error')

    return redirect(url_for('room.booking'))


@room_bp.route('/get-rooms/<floor>')
@login_required
def get_rooms(floor):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT room_number FROM floors_rooms WHERE floor_name = ?', (floor,))
    rooms = cursor.fetchall()
    conn.close()

    return jsonify({'rooms': [r['room_number'] for r in rooms]})

@room_bp.route('/update-checkout', methods=['POST'])
@login_required
def update_checkout():
    booking_id = request.form.get('booking_id')
    new_checkout = request.form.get('check_out')

    if not booking_id or not new_checkout:
        flash('Invalid data for updating check-out date.', 'error')
        return redirect(url_for('room.booking'))

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE room_book SET check_out = ? WHERE id = ?', (new_checkout, booking_id))
        conn.commit()
        flash('Check-out date updated successfully.', 'success')
    except Exception as e:
        flash(f'Error updating check-out date: {str(e)}', 'error')
    finally:
        conn.close()

    return redirect(url_for('room.booking'))


@room_bp.route('/bill')
@login_required
def bill():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM room_book ORDER BY id DESC')
    bookings = cursor.fetchall()

    # Calculate stayed days and room charges (assuming price per day is fixed or can be derived)
    # For demonstration, assume fixed price per day per room type
    price_per_day_map = {
        'Single': 1000,
        'Double': 1500,
        'Suite': 2500
    }

    bookings_with_billing = []
    from datetime import datetime
    for booking in bookings:
        check_in = datetime.strptime(booking['check_in'], '%Y-%m-%d')
        check_out = datetime.strptime(booking['check_out'], '%Y-%m-%d')
        # Calculate number of days between check-in and check-out
        num_days = (check_out - check_in).days
        if num_days <= 0:
            num_days = 1  # minimum 1 day charge

        room_price_per_day = price_per_day_map.get(booking['room_type'], 1000)
        room_charges = num_days * room_price_per_day
        total_payment = room_charges

        booking_dict = dict(booking)
        booking_dict['stayed_days'] = num_days
        booking_dict['room_charges'] = room_charges
        booking_dict['total_payment'] = total_payment

        bookings_with_billing.append(booking_dict)

    conn.close()
    return render_template('room/bill.html', bookings=bookings_with_billing)
