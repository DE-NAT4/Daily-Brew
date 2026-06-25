import pandas as pd
import psycopg2
import os

transactions_path = "Data/processed/cleaned_transactions.csv"
items_path = "Data/processed/transaction_items.csv"

conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432"),
    database=os.getenv("DB_NAME", "solo_cafe"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD")
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
