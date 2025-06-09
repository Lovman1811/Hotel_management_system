from flask_login import UserMixin
from database import get_db
import sqlite3


class User(UserMixin):
    def __init__(self, id, name, emp_id, department, user_type):
        self.id = id
        self.name = name
        self.emp_id = emp_id
        self.department = department
        self.user_type = user_type

    @staticmethod
    def get(user_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admin_emp WHERE id = ?', (user_id,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            return User(
                id=user_data['id'],
                name=user_data['name'],
                emp_id=user_data['emp_id'],
                department=user_data['department'],
                user_type=user_data['type']
            )
        return None

    @staticmethod
    def authenticate(emp_id, password):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admin_emp WHERE emp_id = ? AND password = ?', (emp_id, password))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            return User(
                id=user_data['id'],
                name=user_data['name'],
                emp_id=user_data['emp_id'],
                department=user_data['department'],
                user_type=user_data['type']
            )
        return None


class Guest:
    @staticmethod
    def get_all():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM guest ORDER BY ref DESC')
        guests = cursor.fetchall()
        conn.close()
        return guests

    @staticmethod
    def get_by_id(ref):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM guest WHERE ref = ?', (ref,))
        guest = cursor.fetchone()
        conn.close()
        return guest

    @staticmethod
    def create(data):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO guest (ref, name, guest, id_type, id_no, gender, age, contact, address, images)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)
        conn.commit()
        conn.close()

    @staticmethod
    def update(ref, data):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE guest SET name=?, guest=?, id_type=?, id_no=?, gender=?, age=?, contact=?, address=?, images=?
            WHERE ref=?
        ''', data + (ref,))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(ref):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM guest WHERE ref = ?', (ref,))
        conn.commit()
        conn.close()


class Staff:
    @staticmethod
    def get_all():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM staff_detail ORDER BY emp_id')
        staff = cursor.fetchall()
        conn.close()
        return staff

    @staticmethod
    def get_by_id(emp_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM staff_detail WHERE emp_id = ?', (emp_id,))
        staff = cursor.fetchone()
        conn.close()
        return staff

    @staticmethod
    def create(data):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO staff_detail (emp_id, full_name, id_type, id_number, gender, age, contact, address, department, designation, joining_date, image, salary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)
        conn.commit()
        conn.close()

    @staticmethod
    def update(emp_id, data):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE staff_detail SET full_name=?, id_type=?, id_number=?, gender=?, age=?, contact=?, address=?, department=?, designation=?, joining_date=?, image=?, salary=?
            WHERE emp_id=?
        ''', data + (emp_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def delete(emp_id):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM staff_detail WHERE emp_id = ?', (emp_id,))
        conn.commit()
        conn.close()
