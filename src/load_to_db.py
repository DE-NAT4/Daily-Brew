import pandas as pd
import psycopg2

transactions_path = "data/processed/cleaned_transactions.csv"
items_path = "data/processed/transaction_items.csv"

conn = psycopg2.connect(
    host="192.168.99.213",
    port="5432",
    database="solo_cafe",
    user="postgres",
    password="mysecretpassword"
)

cursor = conn.cursor()

cursor.execute("TRUNCATE TABLE transaction_items, transactions;")

transactions_df = pd.read_csv(transactions_path)

for _, row in transactions_df.iterrows():
    cursor.execute("""
        INSERT INTO transactions (
            transaction_id,
            branch,
            total_amount,
            payment_method,
            transaction_date,
            transaction_time
        )
        VALUES (%s, %s, %s, %s, %s, %s);
    """, (
        row["transaction_id"],
        row["branch"],
        row["total_amount"],
        row["payment_method"],
        pd.to_datetime(row["transaction_date"], format="%d/%m/%Y").date(),
        row["transaction_time"]
    ))

items_df = pd.read_csv(items_path)

for _, row in items_df.iterrows():
    cursor.execute("""
        INSERT INTO transaction_items (
            transaction_item_id,
            transaction_id,
            item_name,
            item_price
        )
        VALUES (%s, %s, %s, %s);
    """, (
        row["transaction_item_id"],
        row["transaction_id"],
        row["item_name"],
        row["item_price"]
    ))

conn.commit()

cursor.close()
conn.close()

print("Data loaded into database successfully.")
