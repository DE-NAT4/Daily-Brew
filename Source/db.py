import psycopg2
from dotenv import load_dotenv
import os

def db_import(transactions_list):

    load_dotenv()

    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("DB_PORT")
    )

    cursor = conn.cursor()

    for transaction in transactions_list:

        # -------------------------
        # INSERT ORDER (ONCE)
        # -------------------------
        cursor.execute("""
            INSERT INTO orders (
                customer_name,
                customer_address,
                customer_phone,
                courier_id,
                status_id
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING order_id;
        """, (
            transaction['customer_name'],
            'none',
            '0',
            1,
            1
        ))

        order_id = cursor.fetchone()[0]

        # -------------------------
        # SPLIT ITEMS
        # -------------------------
        item_raw_list = transaction["items"].split(", ")

        for item in item_raw_list:

            itemised = item.split(" - ")

            product_name = itemised[0].strip()

            print(f"Product name: {repr(product_name)}")

            # -------------------------
            # FIND PRODUCT
            # -------------------------
            cursor.execute("""
                SELECT product_id
                FROM products
                WHERE name = %s;
            """, (product_name,))

            result = cursor.fetchone()

            if result is None:
                print(f"⚠ Product not found: {product_name}")
                continue

            product_id = result[0]

            # -------------------------
            # INSERT ORDER ITEM
            # -------------------------
            cursor.execute("""
                INSERT INTO order_items (
                    order_id,
                    product_id,
                    quantity
                )
                VALUES (%s, %s, %s);
            """, (
                order_id,
                product_id,
                1
            ))
            conn.commit()
    conn.close()