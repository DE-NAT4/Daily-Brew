CREATE SCHEMA IF NOT EXISTS daily_brew_group;

CREATE TABLE IF NOT EXISTS daily_brew_group.transactions (
    transaction_id VARCHAR(36) PRIMARY KEY,
    branch VARCHAR(100),
    total_amount DECIMAL(10, 2),
    payment_method VARCHAR(50),
    transaction_date DATE,
    transaction_time TIME
);

CREATE TABLE IF NOT EXISTS daily_brew_group.transaction_items (
    transaction_item_id VARCHAR(36) PRIMARY KEY,
    transaction_id VARCHAR(36),
    item_name VARCHAR(255),
    item_price DECIMAL(10, 2)
);
