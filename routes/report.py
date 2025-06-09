from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from database import get_db

report_bp = Blueprint('report', __name__)


@report_bp.route('/guest-report')
@login_required
def guest_report():
    conn = get_db()
    cursor = conn.cursor()

    # Get all guests with their booking details
    cursor.execute('''
        SELECT g.ref, g.name, g.guest, g.id_type, g.id_no, g.gender, g.age, g.contact, g.address,
               rb.room_type, rb.floor, rb.room, rb.check_in, rb.check_out
        FROM guest g
        LEFT JOIN room_book rb ON g.contact = rb.contact
        ORDER BY g.ref DESC
    ''')
    guests = cursor.fetchall()
    conn.close()

    return render_template('report/guest_report.html', guests=guests)


@report_bp.route('/staff-report')
@login_required
def staff_report():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM staff_detail ORDER BY emp_id')
    staff = cursor.fetchall()
    conn.close()

    return render_template('report/staff_report.html', staff=staff)


@report_bp.route('/search-guest-report')
@login_required
def search_guest_report():
    search_type = request.args.get('type', 'name')
    search_query = request.args.get('q', '')

    conn = get_db()
    cursor = conn.cursor()

    if search_type == 'name':
        cursor.execute('''
            SELECT g.ref, g.name, g.guest, g.id_type, g.id_no, g.gender, g.age, g.contact, g.address,
                   rb.room_type, rb.floor, rb.room, rb.check_in, rb.check_out
            FROM guest g
            LEFT JOIN room_book rb ON g.contact = rb.contact
            WHERE g.name LIKE ?
            ORDER BY g.ref DESC
        ''', (f'%{search_query}%',))
    elif search_type == 'contact':
        cursor.execute('''
            SELECT g.ref, g.name, g.guest, g.id_type, g.id_no, g.gender, g.age, g.contact, g.address,
                   rb.room_type, rb.floor, rb.room, rb.check_in, rb.check_out
            FROM guest g
            LEFT JOIN room_book rb ON g.contact = rb.contact
            WHERE g.contact LIKE ?
            ORDER BY g.ref DESC
        ''', (f'%{search_query}%',))
    else:
        cursor.execute('''
            SELECT g.ref, g.name, g.guest, g.id_type, g.id_no, g.gender, g.age, g.contact, g.address,
                   rb.room_type, rb.floor, rb.room, rb.check_in, rb.check_out
            FROM guest g
            LEFT JOIN room_book rb ON g.contact = rb.contact
            ORDER BY g.ref DESC
        ''')

    guests = cursor.fetchall()
    conn.close()

    return render_template('report/guest_report.html', guests=guests, search_type=search_type,
                           search_query=search_query)


@report_bp.route('/search-staff-report')
@login_required
def search_staff_report():
    search_type = request.args.get('type', 'name')
    search_query = request.args.get('q', '')

    conn = get_db()
    cursor = conn.cursor()

    if search_type == 'name':
        cursor.execute('SELECT * FROM staff_detail WHERE full_name LIKE ? ORDER BY emp_id', (f'%{search_query}%',))
    elif search_type == 'contact':
        cursor.execute('SELECT * FROM staff_detail WHERE contact LIKE ? ORDER BY emp_id', (f'%{search_query}%',))
    else:
        cursor.execute('SELECT * FROM staff_detail ORDER BY emp_id')

    staff = cursor.fetchall()
    conn.close()

    return render_template('report/staff_report.html', staff=staff, search_type=search_type, search_query=search_query)
