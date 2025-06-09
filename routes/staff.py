from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import Staff
from database import get_db
import os
from werkzeug.utils import secure_filename
from config import Config

staff_bp = Blueprint('staff', __name__)


@staff_bp.route('/')
@login_required
def index():
    staff = Staff.get_all()
    return render_template('staff/index.html', staff=staff)


@staff_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        # Generate employee ID
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM staff_detail')
        count = cursor.fetchone()[0]
        emp_id = f"EMP{count + 1:04d}"

        # Handle file upload
        image_filename = 'default_image.jpeg'
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                image_filename = f"{request.form['full_name']}_{emp_id}_{filename}"
                file.save(os.path.join(Config.UPLOAD_FOLDER, 'staff_images', image_filename))

        data = (
            emp_id,
            request.form['full_name'],
            request.form['id_type'],
            request.form['id_number'],
            request.form['gender'],
            request.form['age'],
            request.form['contact'],
            request.form['address'],
            request.form['department'],
            request.form['designation'],
            request.form['joining_date'],
            image_filename,
            float(request.form['salary'])
        )

        try:
            Staff.create(data)
            flash('Staff member added successfully!', 'success')
            return redirect(url_for('staff.index'))
        except Exception as e:
            flash(f'Error adding staff: {str(e)}', 'error')

    # Get salary data for departments
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT DISTINCT department FROM salary')
        departments = cursor.fetchall()
    except Exception as e:
        departments = []
        flash(f'Error fetching departments: {str(e)}', 'error')
    finally:
        conn.close()

    return render_template('staff/add.html', departments=departments)


@staff_bp.route('/edit/<emp_id>', methods=['GET', 'POST'])
@login_required
def edit(emp_id):
    staff_member = Staff.get_by_id(emp_id)
    if not staff_member:
        flash('Staff member not found!', 'error')
        return redirect(url_for('staff.index'))

    if request.method == 'POST':
        # Handle file upload
        image_filename = staff_member['image']
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                image_filename = f"{request.form['full_name']}_{emp_id}_{filename}"
                file.save(os.path.join(Config.UPLOAD_FOLDER, 'staff_images', image_filename))

        data = (
            request.form['full_name'],
            request.form['id_type'],
            request.form['id_number'],
            request.form['gender'],
            request.form['age'],
            request.form['contact'],
            request.form['address'],
            request.form['department'],
            request.form['designation'],
            request.form['joining_date'],
            image_filename,
            float(request.form['salary'])
        )

        try:
            Staff.update(emp_id, data)
            flash('Staff member updated successfully!', 'success')
            return redirect(url_for('staff.index'))
        except Exception as e:
            flash(f'Error updating staff: {str(e)}', 'error')

    # Get salary data for departments
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT DISTINCT department FROM salary')
        departments = cursor.fetchall()
    except Exception as e:
        departments = []
        flash(f'Error fetching departments: {str(e)}', 'error')
    finally:
        conn.close()

    return render_template('staff/edit.html', staff=staff_member, departments=departments)


@staff_bp.route('/delete/<emp_id>')
@login_required
def delete(emp_id):
    try:
        Staff.delete(emp_id)
        flash('Staff member deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting staff: {str(e)}', 'error')
    return redirect(url_for('staff.index'))


@staff_bp.route('/get-designations/<department>')
@login_required
def get_designations(department):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT designation, salary FROM salary WHERE department = ?', (department,))
    designations = cursor.fetchall()
    conn.close()

    return {
        'designations': [{'designation': d['designation'], 'salary': d['salary']} for d in designations]
    }
