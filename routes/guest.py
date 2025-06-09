from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from models import Guest
from database import get_db
import os
from werkzeug.utils import secure_filename
from config import Config

guest_bp = Blueprint('guest', __name__)


@guest_bp.route('/')
@login_required
def index():
    guests = Guest.get_all()
    return render_template('guest/index.html', guests=guests)


@guest_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        # Get next reference ID
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT MAX(ref) FROM guest')
        max_ref = cursor.fetchone()[0]
        ref = (max_ref + 1) if max_ref else 1001

        # Handle file upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                image_filename = f"{request.form['name']}_{ref}_{filename}"
                file.save(os.path.join(Config.UPLOAD_FOLDER, 'guest_images', image_filename))

        data = (
            ref,
            request.form['name'],
            int(request.form['guest_count']),
            request.form['id_type'],
            request.form['id_number'],
            request.form['gender'],
            request.form['age'],
            request.form['contact'],
            request.form['address'],
            image_filename
        )

        try:
            Guest.create(data)
            flash('Guest added successfully!', 'success')
            return redirect(url_for('room.booking'))
        except Exception as e:
            flash(f'Error adding guest: {str(e)}', 'error')

    return render_template('guest/add.html')


@guest_bp.route('/edit/<int:ref>', methods=['GET', 'POST'])
@login_required
def edit(ref):
    guest = Guest.get_by_id(ref)
    if not guest:
        flash('Guest not found!', 'error')
        return redirect(url_for('guest.index'))

    if request.method == 'POST':
        # Handle file upload
        image_filename = guest['images']
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                image_filename = f"{request.form['name']}_{ref}_{filename}"
                file.save(os.path.join(Config.UPLOAD_FOLDER, 'guest_images', image_filename))

        data = (
            request.form['name'],
            int(request.form['guest_count']),
            request.form['id_type'],
            request.form['id_number'],
            request.form['gender'],
            request.form['age'],
            request.form['contact'],
            request.form['address'],
            image_filename
        )

        try:
            Guest.update(ref, data)
            flash('Guest updated successfully!', 'success')
            return redirect(url_for('guest.index'))
        except Exception as e:
            flash(f'Error updating guest: {str(e)}', 'error')

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT DISTINCT floor_name FROM floors_rooms')
        floors = [row['floor_name'] for row in cursor.fetchall()]
    except Exception as e:
        floors = []
        flash(f'Error fetching floors: {str(e)}', 'error')
    finally:
        conn.close()

    return render_template('guest/edit.html', guest=guest, floors=floors)


@guest_bp.route('/delete/<int:ref>')
@login_required
def delete(ref):
    try:
        Guest.delete(ref)
        flash('Guest deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting guest: {str(e)}', 'error')
    return redirect(url_for('guest.index'))


@guest_bp.route('/search')
@login_required
def search():
    search_type = request.args.get('type', 'name')
    search_query = request.args.get('q', '')

    conn = get_db()
    cursor = conn.cursor()

    if search_type == 'name':
        cursor.execute('SELECT * FROM guest WHERE name LIKE ? ORDER BY ref DESC', (f'%{search_query}%',))
    elif search_type == 'contact':
        cursor.execute('SELECT * FROM guest WHERE contact LIKE ? ORDER BY ref DESC', (f'%{search_query}%',))
    else:
        cursor.execute('SELECT * FROM guest ORDER BY ref DESC')

    guests = cursor.fetchall()
    conn.close()

    return render_template('guest/index.html', guests=guests, search_type=search_type, search_query=search_query)
