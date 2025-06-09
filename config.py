import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hotel_management.db')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)

    # Create upload directories if they don't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'guest_images'), exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'staff_images'), exist_ok=True)
