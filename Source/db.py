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

    for items in transactions_list:

        # Insert order
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
            items['customer_name'],
            'none',
            '0',
            0,
            0
        ))

        order_id = cursor.fetchone()[0]

        # Split items
        item_raw_list = items["items"].split(", ")

        for item in item_raw_list:
            itemised = item.split(" - ")

            product_name = itemised[0]

            # Get product_id
            cursor.execute("""
                SELECT product_id
                FROM products
                WHERE product_name = %s;
            """, (product_name,))

            product_id = cursor.fetchone()[0]

            # INSERT EACH ITEM (IMPORTANT FIX)
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id)
                VALUES (%s, %s);
            """, (order_id, product_id))

    conn.commit()
    conn.close()