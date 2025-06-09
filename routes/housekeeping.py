from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from database import get_db

housekeeping_bp = Blueprint('housekeeping', __name__)


@housekeeping_bp.route('/')
@login_required
def index():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM housekeeping ORDER BY floor, room_number')
    rooms = cursor.fetchall()
    conn.close()

    return render_template('housekeeping/index.html', rooms=rooms)


@housekeeping_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        data = (
            request.form['floor'],
            request.form['room_number'],
            request.form['status']
        )

        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO housekeeping (floor, room_number, status)
                VALUES (?, ?, ?)
            ''', data)
            conn.commit()
            conn.close()

            flash('Room status added successfully!', 'success')
            return redirect(url_for('housekeeping.index'))
        except Exception as e:
            flash(f'Error adding room status: {str(e)}', 'error')

    # Get available floors and rooms
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT floor_name FROM floors_rooms ORDER BY floor_name')
    floors = cursor.fetchall()
    conn.close()

    return render_template('housekeeping/add.html', floors=floors)


@housekeeping_bp.route('/edit/<int:room_id>', methods=['GET', 'POST'])
@login_required
def edit(room_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM housekeeping WHERE id = ?', (room_id,))
    room = cursor.fetchone()

    if not room:
        flash('Room not found!', 'error')
        return redirect(url_for('housekeeping.index'))

    if request.method == 'POST':
        data = (
            request.form['floor'],
            request.form['room_number'],
            request.form['status'],
            room_id
        )

        try:
            cursor.execute('''
                UPDATE housekeeping 
                SET floor=?, room_number=?, status=?
                WHERE id=?
            ''', data)
            conn.commit()
            conn.close()

            flash('Room status updated successfully!', 'success')
            return redirect(url_for('housekeeping.index'))
        except Exception as e:
            flash(f'Error updating room status: {str(e)}', 'error')

    # Get available floors
    cursor.execute('SELECT DISTINCT floor_name FROM floors_rooms ORDER BY floor_name')
    floors = cursor.fetchall()
    conn.close()

    return render_template('housekeeping/edit.html', room=room, floors=floors)


@housekeeping_bp.route('/delete/<int:room_id>')
@login_required
def delete(room_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM housekeeping WHERE id = ?', (room_id,))
        conn.commit()
        conn.close()

        flash('Room status deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting room status: {str(e)}', 'error')

    return redirect(url_for('housekeeping.index'))


@housekeeping_bp.route('/get-rooms/<floor>')
@login_required
def get_rooms(floor):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT room_number FROM floors_rooms WHERE floor_name = ?', (floor,))
    rooms = cursor.fetchall()
    conn.close()

    return jsonify({'rooms': [r['room_number'] for r in rooms]})


@housekeeping_bp.route('/update-status', methods=['POST'])
@login_required
def update_status():
    room_id = request.form['room_id']
    new_status = request.form['status']

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE housekeeping SET status = ? WHERE id = ?', (new_status, room_id))
        conn.commit()
        conn.close()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
