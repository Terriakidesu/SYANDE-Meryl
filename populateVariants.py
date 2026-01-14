
import random

from src.helpers import Database

db = Database()


def main():

    shoes = db.fetchAll("SELECT * FROM shoes")

    sizes = db.fetchAll("SELECT * FROM sizes")
    sizes_count = len(sizes) - 1

    for shoe in shoes:
        shoe_id = shoe["shoe_id"]
        variants = db.fetchAll(
            "SELECT * FROM variants where shoe_id = %s", (shoe_id,))

        if variants:
            continue

        size_count = random.randint(3, 8)
        size_start = random.randint(
            0, min(sizes_count, sizes_count - size_count))

        values = []

        for size_i in range(size_start, size_start + size_count):
            stock_range = random.randint(1, 500)
            size_id = sizes[size_i]["size_id"]
            variant = (shoe_id, size_id, stock_range)

            values.append(variant)
    
        db.commitMany("INSERT INTO variants (shoe_id, size_id, variant_stock) VALUES (%s, %s, %s)", values)


if __name__ == "__main__":
    main()
