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

        ### INSERT ORDER
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

        ###SPLIT ITEMS
        item_raw_list = transaction["items"].split(", ")

        items_dict = {}

        for item in item_raw_list:
            itemised = item.split(" - ")

            product_name = itemised[0].strip()

            ###check if product is in the DB

            cursor.execute("""
                SELECT product_id
                FROM products
                WHERE name = %s;
            """, (product_name,))

            result = cursor.fetchone()

            ####If the item is not in the DB, insert it
            if result is None:
                cursor.execute(
                    """
                    INSERT INTO products (
                        name,
                        price,
                        quantity
                    )
                    VALUES (%s, %s, %s);
                    """,
                    (
                        product_name,
                        0,
                        10
                    )
                )
            items_dict[product_name] = items_dict.get(product_name, 0) + 1

        ###loop through the dictionary made for each order
        for product_name, quantity in items_dict.items():

            cursor.execute("""
            SELECT product_id
            FROM products
            WHERE name = %s;
            """, (product_name,))

            result = cursor.fetchone()
            
            if result is None:
                print(f"⚠ Product not found: {product_name}")
                continue
            else:
                product_id = result[0]
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
                    items_dict[product_name]
                ))
                conn.commit()
    conn.close()