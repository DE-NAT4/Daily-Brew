CREATE TABLE transactions (
    transaction_id UUID PRIMARY KEY,
    branch VARCHAR(100),
    total_amount NUMERIC(10, 2),
    payment_method VARCHAR(20),
    transaction_date DATE,
    transaction_time TIME
);

CREATE TABLE transaction_items (
    transaction_item_id UUID PRIMARY KEY,
    transaction_id UUID REFERENCES transactions(transaction_id),
    item_name VARCHAR(255),
    item_price NUMERIC(10, 2)
);