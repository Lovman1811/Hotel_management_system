from database import init_db, init_restaurant_orders_table

def main():
    print("Initializing database...")
    init_db()
    init_restaurant_orders_table()
    print("Database initialized successfully.")

if __name__ == "__main__":
    main()
