from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required
from datetime import datetime
import os
import qrcode
from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas

restaurant_bp = Blueprint('restaurant', __name__)

# Menu items
MENU_ITEMS = {
    "Starters": {
        "1": {"name": "Vegetable Spring Rolls", "price": 50},
        "2": {"name": "Cheese Nachos", "price": 90},
        "3": {"name": "Garlic Bread", "price": 130},
    },
    "Main Courses": {
        "1": {"name": "Chicken Alfredo", "price": 350},
        "2": {"name": "Spaghetti Bolognese", "price": 290},
        "3": {"name": "Grilled Salmon", "price": 160},
    },
    "Desserts": {
        "1": {"name": "Chocolate Cake", "price": 600},
        "2": {"name": "Cheesecake", "price": 540},
        "3": {"name": "Ice Cream", "price": 290},
    },
    "Drinks": {
        "1": {"name": "Coca-Cola", "price": 80},
        "2": {"name": "Sprite", "price": 80},
        "3": {"name": "Lemonade", "price": 60},
    },
}


@restaurant_bp.route('/')
@login_required
def index():
    return render_template('restaurant/index.html', menu=MENU_ITEMS)


@restaurant_bp.route('/add-to-order', methods=['POST'])
@login_required
def add_to_order():
    item = {
        'name': request.form['item_name'],
        'price': float(request.form['price']),
        'quantity': int(request.form['quantity']),
        'total': float(request.form['price']) * int(request.form['quantity'])
    }

    # Save order to database linked to booking_id
    booking_id = request.form.get('booking_id')
    if not booking_id:
        flash('Booking ID is required to add order', 'error')
        return redirect(url_for('restaurant.index'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO restaurant_orders (booking_id, item_name, quantity, price, total, order_date)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    ''', (booking_id, item['name'], item['quantity'], item['price'], item['total']))
    conn.commit()
    conn.close()

    flash('Item added to order successfully!', 'success')
    return redirect(url_for('restaurant.index'))


@restaurant_bp.route('/remove-from-order/<int:order_id>')
@login_required
def remove_from_order(order_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM restaurant_orders WHERE id = ?', (order_id,))
    conn.commit()
    conn.close()

    flash('Item removed from order.', 'info')
    return redirect(url_for('restaurant.index'))


@restaurant_bp.route('/clear-order/<int:booking_id>')
@login_required
def clear_order(booking_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM restaurant_orders WHERE booking_id = ?', (booking_id,))
    conn.commit()
    conn.close()

    flash('Order cleared.', 'info')
    return redirect(url_for('restaurant.index'))


@restaurant_bp.route('/generate-bill/<int:booking_id>')
@login_required
def generate_bill(booking_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM restaurant_orders WHERE booking_id = ?', (booking_id,))
    orders = cursor.fetchall()

    if not orders:
        flash('No items in order!', 'error')
        return redirect(url_for('restaurant.index'))

    total_amount = sum(order['total'] for order in orders)

    # Generate QR code for payment
    upi_id = "lds822001-1@okicici"
    qr_data = f"upi://pay?pa={upi_id}&am={total_amount:.2f}"

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)

    qr_path = os.path.join('static', 'temp', f'qr_code_{booking_id}.png')
    os.makedirs(os.path.dirname(qr_path), exist_ok=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(qr_path)

    bill_data = {
        'booking_id': booking_id,
        'order': orders,
        'total': total_amount,
        'date': datetime.now().strftime('%d/%m/%Y (%A)\n%H:%M:%S'),
        'qr_path': qr_path
    }

    return render_template('restaurant/bill.html', **bill_data)
