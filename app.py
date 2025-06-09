from flask import Flask, render_template, redirect, url_for, session, flash
from flask_login import LoginManager, login_required, current_user
from config import Config
from database import init_db, get_db
import os

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

# Initialize database
init_db()

# Import and register blueprints
from routes.auth import auth_bp
from routes.main import main_bp
from routes.guest import guest_bp
from routes.room import room_bp
from routes.staff import staff_bp
from routes.report import report_bp
from routes.restaurant import restaurant_bp
from routes.housekeeping import housekeeping_bp
from routes.account import account_bp
from routes.api import api_bp
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(main_bp)
app.register_blueprint(guest_bp, url_prefix='/guest')
app.register_blueprint(room_bp, url_prefix='/room')
app.register_blueprint(staff_bp, url_prefix='/staff')
app.register_blueprint(report_bp, url_prefix='/report')
app.register_blueprint(restaurant_bp, url_prefix='/restaurant')
app.register_blueprint(housekeeping_bp, url_prefix='/housekeeping')
app.register_blueprint(account_bp, url_prefix='/account')

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.get(user_id)

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True)
