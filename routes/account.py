from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from database import get_db
from datetime import date

account_bp = Blueprint('account', __name__)


@account_bp.route('/')
@login_required
def index():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT a.*, s.full_name, s.department, s.designation
        FROM account a
        LEFT JOIN staff_detail s ON a.emp_id = s.emp_id
        ORDER BY a.date DESC
    ''')
    accounts = cursor.fetchall()
    conn.close()

    return render_template('account/index.html', accounts=accounts)


@account_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        # Calculate net pay
        basic_salary = float(request.form['basic_salary'])
        allowances = float(request.form['allowances'])
        deductions = float(request.form['deductions'])
        net_pay = basic_salary + allowances - deductions

        data = (
            request.form['emp_id'],
            request.form['full_name'],
            request.form['id_type'],
            request.form['id_number'],
            request.form['gender'],
            request.form['contact'],
            request.form['address'],
            request.form['pay_date'],
            basic_salary,
            allowances,
            deductions,
            net_pay
        )

        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO account (emp_id, full_name, id_type, id_number, gender, contact, address, date, basic_salary, allowances, deductions, net_pay)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', data)
            conn.commit()
            conn.close()

            flash('Account record added successfully!', 'success')
            return redirect(url_for('account.index'))
        except Exception as e:
            flash(f'Error adding account record: {str(e)}', 'error')

    # Get staff list for dropdown
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT emp_id, full_name FROM staff_detail ORDER BY full_name')
    staff_list = cursor.fetchall()
    conn.close()

    return render_template('account/add.html', staff_list=staff_list, today=date.today().isoformat())


@account_bp.route('/edit/<int:account_id>', methods=['GET', 'POST'])
@login_required
def edit(account_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM account WHERE id = ?', (account_id,))
    account = cursor.fetchone()

    if not account:
        flash('Account record not found!', 'error')
        return redirect(url_for('account.index'))

    if request.method == 'POST':
        # Calculate net pay
        basic_salary = float(request.form['basic_salary'])
        allowances = float(request.form['allowances'])
        deductions = float(request.form['deductions'])
        net_pay = basic_salary + allowances - deductions

        data = (
            request.form['emp_id'],
            request.form['full_name'],
            request.form['id_type'],
            request.form['id_number'],
            request.form['gender'],
            request.form['contact'],
            request.form['address'],
            request.form['pay_date'],
            basic_salary,
            allowances,
            deductions,
            net_pay,
            account_id
        )

        try:
            cursor.execute('''
                UPDATE account 
                SET emp_id=?, full_name=?, id_type=?, id_number=?, gender=?, contact=?, address=?, date=?, basic_salary=?, allowances=?, deductions=?, net_pay=?
                WHERE id=?
            ''', data)
            conn.commit()
            conn.close()

            flash('Account record updated successfully!', 'success')
            return redirect(url_for('account.index'))
        except Exception as e:
            flash(f'Error updating account record: {str(e)}', 'error')

    # Get staff list for dropdown
    cursor.execute('SELECT emp_id, full_name FROM staff_detail ORDER BY full_name')
    staff_list = cursor.fetchall()
    conn.close()

    return render_template('account/edit.html', account=account, staff_list=staff_list)


@account_bp.route('/delete/<int:account_id>')
@login_required
def delete(account_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM account WHERE id = ?', (account_id,))
        conn.commit()
        conn.close()

        flash('Account record deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting account record: {str(e)}', 'error')

    return redirect(url_for('account.index'))


@account_bp.route('/fetch-staff/<emp_id>')
@login_required
def fetch_staff(emp_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM staff_detail WHERE emp_id = ?', (emp_id,))
    staff = cursor.fetchone()
    conn.close()

    if staff:
        return jsonify({
            'success': True,
            'data': {
                'full_name': staff['full_name'],
                'id_type': staff['id_type'],
                'id_number': staff['id_number'],
                'gender': staff['gender'],
                'contact': staff['contact'],
                'address': staff['address'],
                'salary': staff['salary']
            }
        })
    else:
        return jsonify({'success': False, 'error': 'Staff not found'})


@account_bp.route('/calculate-net-pay', methods=['POST'])
@login_required
def calculate_net_pay():
    try:
        basic_salary = float(request.form['basic_salary'])
        allowances = float(request.form['allowances'])
        deductions = float(request.form['deductions'])
        net_pay = basic_salary + allowances - deductions

        return jsonify({'success': True, 'net_pay': net_pay})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
