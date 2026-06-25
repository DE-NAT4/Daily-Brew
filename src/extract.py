import pandas as pd
import uuid

file_path = "data/raw/leeds_28-03-2025_09-00-00.csv"

column_names = [
    "transaction_datetime",
    "branch",
    "customer_name",
    "items",
    "total_amount",
    "payment_method",
    "card_number"
]

df = pd.read_csv(file_path, header=None, names=column_names)

clean_df = df.drop(columns=["customer_name", "card_number"])

clean_df[["transaction_date", "transaction_time"]] = clean_df["transaction_datetime"].str.split(" ", expand=True)
clean_df = clean_df.drop(columns=["transaction_datetime"])

clean_df["branch"] = clean_df["branch"].str.lower()
clean_df["items"] = clean_df["items"].str.lower()
clean_df["payment_method"] = clean_df["payment_method"].str.lower()

clean_df["transaction_id"] = [str(uuid.uuid4()) for _ in range(len(clean_df))]

transactions_df = clean_df.drop(columns=["items"])

transactions_output_path = "data/processed/cleaned_transactions.csv"

transactions_df.to_csv(transactions_output_path, index=False)

transaction_items = []

for index, row in clean_df.iterrows():
    items_list = row["items"].split(", ")

    for item in items_list:
        item_name, item_price = item.rsplit(" - ", 1)

        transaction_items.append({
            "transaction_item_id": str(uuid.uuid4()),
            "transaction_id": row["transaction_id"],
            "item_name": item_name,
            "item_price": item_price
        })

transaction_items_df = pd.DataFrame(transaction_items)

items_output_path = "data/processed/transaction_items.csv"

transaction_items_df.to_csv(items_output_path, index=False)

print(transactions_df.head())
print(f"Transaction rows: {len(transactions_df)}")
print(f"Transaction columns: {len(transactions_df.columns)}")
print(f"Transactions file saved to {transactions_output_path}")

print(transaction_items_df.head(10))
print(f"Transaction item rows: {len(transaction_items_df)}")
print(f"Transaction items file saved to {items_output_path}")