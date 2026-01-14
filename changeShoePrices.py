import random

from src.helpers import Database

db = Database()


def main():

    shoes = db.fetchAll(r"SELECT * FROM shoes")

    values = []

    for shoe in shoes:
        shoe_id = shoe["shoe_id"]
        price: float = shoe["shoe_price"] * max(random.random() * 20, 6)

        price -= price - int(price)

        if random.random() <= 0.4:
            price = round(price, -2)

        if random.random() <= 0.2:
            price += .99

        value = (price, shoe_id)

        values.append(value)

    db.commitMany(
        "UPDATE shoes SET shoe_price = %s WHERE shoe_id = %s", values)


if __name__ == "__main__":
    main()
