from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from database import get_db
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

auth_bp = Blueprint('auth', __name__)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_USER = "lds822001@gmail.com"
SMTP_PASSWORD = "mlczcsxnqitvaout"  # Update with app-specific password
OTP_VALIDITY = 300  # 5 minutes in seconds

otp_store = {}  # Temporary store for OTPs: {email: (otp, timestamp)}

def send_otp_email(receiver_email, otp):
    try:
        message = MIMEMultipart()
        message["From"] = SMTP_USER
        message["To"] = receiver_email
        message["Subject"] = "Your Verification OTP"

        body = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); background: linear-gradient(to right, #f8f9fa, #e9ecef);">
            <h2 style="color: #333; text-align: center; border-bottom: 2px solid #007bff; padding-bottom: 15px; margin-bottom: 20px;">Hotel Stay Verification</h2>
            <div style="background-color: white; padding: 20px; border-radius: 8px; text-align: center;">
                <p style="font-size: 16px; color: #555; margin-bottom: 15px;">Your One-Time Password (OTP) is:</p>
                <h1 style="color: #007bff; font-size: 42px; letter-spacing: 5px; font-weight: 700; margin: 25px 0; text-shadow: 0 1px 2px rgba(0,0,0,0.1);">{otp}</h1>
                <p style="font-size: 14px; color: #666; background-color: #f8f9fa; padding: 10px; border-radius: 5px; display: inline-block;">This OTP is valid for <span style="font-weight: bold;">{OTP_VALIDITY // 60} minutes</span></p>
                <p style="font-size: 12px; color: #999; margin-top: 25px;">Please do not share this code with anyone. This OTP is for verification purposes only.</p>
            </div>
            <div style="text-align: center; margin-top: 20px; padding-top: 15px; border-top: 1px solid #dee2e6;">
                <p style="color: #777; font-size: 12px;">© 2025 Hotel Management System. All rights reserved.</p>
            </div>
        </div>
        """
        message.attach(MIMEText(body, "html"))

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, receiver_email, message.as_string())
        return True
    except Exception as e:
        print(f"Failed to send OTP: {str(e)}")
        return False

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        emp_id = request.form['emp_id']
        password = request.form['password']
        user_type = request.form['user_type']

        user = User.authenticate(emp_id, password)
        if user and user.user_type == user_type:
            login_user(user)
            session['user_type'] = user.user_type
            flash(f'Welcome to the {user.department} department!', 'success')
            return redirect(url_for('main.dashboard_html'))
        else:
            flash('Invalid credentials', 'error')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.form
    name = data.get('name')
    email = data.get('email')
    contact = data.get('contact')
    check_in = data.get('check_in')
    check_out = data.get('check_out')
    otp = data.get('otp')

    if not all([name, email, contact, check_in, check_out]):
        flash('Please fill all required fields.', 'error')
        return redirect(url_for('auth.login'))

    # Verify OTP
    stored_otp = otp_store.get(email)
    if not stored_otp or stored_otp[0] != otp:
        flash('Invalid or expired OTP.', 'error')
        return redirect(url_for('auth.login'))

    # Save registration data to database
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO online_bookings (name, email, contact, check_in, check_out)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, email, contact, check_in, check_out))
    conn.commit()
    conn.close()

    # Remove OTP after successful verification
    otp_store.pop(email, None)

    flash('Registration successful! Please wait for confirmation.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    from time import time
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'success': False, 'error': 'Email is required'})

    otp = ''.join(random.choices(string.digits, k=6))
    success = send_otp_email(email, otp)
    if success:
        otp_store[email] = (otp, time())
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Failed to send OTP'})
