import sqlite3
import os
from config import Config


def get_db():
    """Get database connection"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database with tables"""
    conn = get_db()
    cursor = conn.cursor()

    # Create tables
    cursor.executescript('''
        -- Admin/Employee table
        CREATE TABLE IF NOT EXISTS admin_emp (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            emp_id TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            type TEXT NOT NULL,
            password TEXT NOT NULL
        );

        -- Guest table
        CREATE TABLE IF NOT EXISTS guest (
            ref INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            guest INTEGER NOT NULL,
            id_type TEXT NOT NULL,
            id_no TEXT NOT NULL,
            gender TEXT NOT NULL,
            age TEXT NOT NULL,
            contact TEXT NOT NULL,
            address TEXT NOT NULL,
            images TEXT
        );

        -- Staff detail table
        CREATE TABLE IF NOT EXISTS staff_detail (
            emp_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            id_type TEXT NOT NULL,
            id_number TEXT NOT NULL,
            gender TEXT NOT NULL,
            age TEXT NOT NULL,
            contact TEXT NOT NULL,
            address TEXT NOT NULL,
            department TEXT NOT NULL,
            designation TEXT NOT NULL,
            joining_date TEXT NOT NULL,
            image TEXT,
            salary REAL
        );

        -- Room booking table
        CREATE TABLE IF NOT EXISTS room_book (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact TEXT NOT NULL,
            room_type TEXT NOT NULL,
            floor TEXT NOT NULL,
            room TEXT NOT NULL,
            check_in TEXT NOT NULL,
            check_out TEXT NOT NULL
        );

        -- Floors and rooms table
        CREATE TABLE IF NOT EXISTS floors_rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            floor_name TEXT NOT NULL,
            room_number TEXT NOT NULL
        );

        -- Housekeeping table
        CREATE TABLE IF NOT EXISTS housekeeping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            floor TEXT NOT NULL,
            room_number TEXT NOT NULL,
            status TEXT NOT NULL
        );

        -- Account table
        CREATE TABLE IF NOT EXISTS account (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            full_name TEXT NOT NULL,
            id_type TEXT NOT NULL,
            id_number TEXT NOT NULL,
            gender TEXT NOT NULL,
            contact TEXT NOT NULL,
            address TEXT NOT NULL,
            date TEXT NOT NULL,
            basic_salary REAL NOT NULL,
            allowances REAL NOT NULL,
            deductions REAL NOT NULL,
            net_pay REAL NOT NULL
        );

        -- Salary table
        CREATE TABLE IF NOT EXISTS salary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            department TEXT NOT NULL,
            designation TEXT NOT NULL,
            salary REAL NOT NULL
        );

        -- Online bookings table
        CREATE TABLE IF NOT EXISTS online_bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            contact TEXT NOT NULL,
            check_in TEXT NOT NULL,
            check_out TEXT NOT NULL,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # Insert default admin user if not exists
    cursor.execute('SELECT COUNT(*) FROM admin_emp WHERE emp_id = ?', ('admin001',))
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO admin_emp (name, emp_id, department, type, password)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Admin', 'admin001', 'Management', 'Admin', 'admin123'))

    # Insert default salary data
    salary_data = [
        ('Front Office/Reception', 'Receptionist', 32000.00),
        ('Front Office/Reception', 'Front Desk Manager', 50000.00),
        ('Front Office/Reception', 'Concierge', 35000.00),
        ('Housekeeping', 'Housekeeper', 25000.00),
        ('Housekeeping', 'Housekeeping Manager', 45000.00),
        ('Housekeeping', 'Laundry Attendant', 20000.00),
        ('Food and Beverage', 'Restaurant Manager', 60000.00),
        ('Accounting/Finance', 'Accountant', 40000.00),
        ('Accounting/Finance', 'Finance Manager', 70000.00),
        ('Accounting/Finance', 'Cashier', 30000.00)
    ]

    cursor.execute('SELECT COUNT(*) FROM salary')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO salary (department, designation, salary)
            VALUES (?, ?, ?)
        ''', salary_data)

    # Insert default rooms data
    rooms_data = []
    floors = [
        ('Ground Floor', ['001', '002', '003', '004', '005']),
        ('1st Floor', ['101', '102', '103', '104', '105']),
        ('2nd Floor', ['201', '202', '203', '204', '205']),
        ('3rd Floor', ['301', '302', '303', '304', '305']),
        ('4th Floor', ['401', '402', '403', '404', '405']),
        ('5th Floor', ['501', '502', '503', '504', '505'])
    ]

    for floor_name, rooms in floors:
        for room in rooms:
            rooms_data.append((floor_name, room))

    cursor.execute('SELECT COUNT(*) FROM floors_rooms')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO floors_rooms (floor_name, room_number)
            VALUES (?, ?)
        ''', rooms_data)

    conn.commit()
    conn.close()

def init_restaurant_orders_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS restaurant_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            total REAL NOT NULL,
            order_date TEXT NOT NULL,
            FOREIGN KEY (booking_id) REFERENCES room_book(id)
        )
    ''')
    conn.commit()
    conn.close()
