
import random
from datetime import datetime, timedelta

from src.helpers import Database

db = Database()

def random_name():
    first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def sequential_date(sale_index, total_sales):
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 12, 31)
    total_days = (end_date - start_date).days
    days_per_sale = total_days / total_sales
    current_days = int(sale_index * days_per_sale)
    return start_date + timedelta(days=current_days)

def main():
    users = db.fetchAll(r'SELECT user_id FROM users')
    user_ids = [user['user_id'] for user in users]

    # Get all variants with stock > 0
    variants = db.fetchAll(r'SELECT * FROM variants WHERE variant_stock > 0')

    if not variants:
        print("No variants with stock available")
        return

    total_sales = 250
    sale_count = 0

    for i in range(total_sales):
        # Random user
        user_id = random.choice(user_ids)

        # Random customer name
        customer_name = random_name()

        # Random number of items (1-5)
        num_items = random.randint(1, 5)
        selected_variants = random.sample(variants, min(num_items, len(variants)))

        total_amount = 0
        sale_items = []

        for variant in selected_variants:
            variant_id = variant['variant_id']
            shoe_id = variant['shoe_id']

            # Get shoe price and markup
            shoe = db.fetchOne(r'SELECT shoe_price, markup FROM shoes WHERE shoe_id = %s', (shoe_id,))
            if not shoe:
                continue
            shoe_price = shoe['shoe_price']
            markup = shoe['markup']

            # Random quantity (1-3, but not more than stock)
            max_qty = min(3, variant['variant_stock'])
            if max_qty < 1:
                continue
            quantity = random.randint(1, max_qty)

            # Calculate price (same as in sales.py)
            price = shoe_price * (1 + markup / 100) * quantity
            total_amount += price

            sale_items.append((variant_id, quantity, price))

        if total_amount == 0:
            continue  # Skip if no items

        # Sequential sales date
        sales_date = sequential_date(sale_count, total_sales)

        # Cash received: total + random change 0-50
        cash_received = total_amount + random.randint(0, 50)
        change_amount = cash_received - total_amount

        # Insert sale
        cursor = db.commitOne(r'INSERT INTO sales (user_id, customer_name, total_amount, cash_received, change_amount, sales_date) VALUES (%s, %s, %s, %s, %s, %s)',
                              (user_id, customer_name, total_amount, cash_received, change_amount, sales_date))
        sale_id = cursor.lastrowid

        # Insert sales_items
        for variant_id, quantity, price in sale_items:
            db.commitOne(r'INSERT INTO sales_items (sale_id, variant_id, quantity, price) VALUES (%s, %s, %s, %s)',
                         (sale_id, variant_id, quantity, price))

            # Update stock
            # db.commitOne(r'UPDATE variants SET variant_stock = variant_stock - %s WHERE variant_id = %s',
            #              (quantity, variant_id))

        sale_count += 1

    print("Sales populated")


if __name__ == "__main__":
    main()
