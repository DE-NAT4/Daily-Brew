# Solo Cafe ETL Project

## What This Project Does

This project processes raw cafe transaction CSV data and removes sensitive customer information before storing the cleaned data.

The project has three main parts:

1. A local proof of concept that loads cleaned data into PostgreSQL.
2. An AWS ETL pipeline that loads cleaned data into Amazon Redshift.
3. Grafana dashboards that visualise sales data and infrastructure metrics.

## Local Pipeline

The local pipeline reads a raw CSV file, cleans it, creates processed CSV files, and loads the data into a local PostgreSQL database.

Steps:

1. Read the raw CSV file.
2. Add column names because the raw CSV has no headers.
3. Remove sensitive data:
   - customer name
   - card number
4. Split transaction date and transaction time.
5. Convert text fields to lowercase.
6. Generate GUIDs for transaction IDs and transaction item IDs.
7. Split purchased items into separate rows.
8. Save processed CSV files.
9. Load processed data into PostgreSQL.

Run the local extract/transform script:

```bash
py src/extract.py
```

Run the local database load script:

```bash
py src/load_to_db.py
```

For the local database load, set the database password in an environment variable instead of writing it in the code:

```powershell
$env:DB_PASSWORD = "your_password_here"
```

## AWS Pipeline

Sprint 2 moves the ETL process into AWS.

The cloud pipeline is:

```text
CSV uploaded to S3
-> S3 triggers Lambda
-> Lambda reads the CSV
-> Lambda removes sensitive data and transforms the rows
-> Lambda loads the cleaned data into Redshift
```

AWS resources used:

- S3 bucket: `daily-brew-group-raw-csv`
- Lambda function: `daily-brew-group-etl-lambda`
- Redshift database: `daily_brew_cafe_db`
- Redshift schema: `daily_brew_group`
- Redshift tables:
  - `daily_brew_group.transactions`
  - `daily_brew_group.transaction_items`

## Data Model

### `daily_brew_group.transactions`

Stores one row per transaction.

Columns:

- `transaction_id`
- `branch`
- `total_amount`
- `payment_method`
- `transaction_date`
- `transaction_time`

### `daily_brew_group.transaction_items`

Stores one row per item bought in a transaction.

Columns:

- `transaction_item_id`
- `transaction_id`
- `item_name`
- `item_price`

One transaction can have many transaction items.

## AWS Files

### `aws/lambda/lambda_function.py`

The Lambda code.

It:

- receives the S3 event
- gets the bucket name and file name
- loads the CSV from S3 using `boto3`
- removes customer name and card number
- splits transaction date and time
- lowercases text fields
- splits purchased items into separate rows
- generates GUIDs
- inserts cleaned rows into Redshift

### `aws/cloudformation/deployment-bucket-stack.yml`

Creates the deployment bucket used for CloudFormation packaging.

This bucket is for deployment files, not raw cafe CSV data.

### `aws/cloudformation/etl-stack.yml`

Creates the ETL resources:

- raw CSV S3 bucket
- Lambda function
- S3 trigger
- permissions for S3 to trigger Lambda

### `aws/scripts/deploy.ps1`

Deploys the ETL CloudFormation stacks from PowerShell.

## Redshift Setup

A separate schema was created for this project:

```sql
CREATE SCHEMA IF NOT EXISTS daily_brew_group;
```

Tables were created in the `daily_brew_group` schema:

```sql
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
```

## Test Result

After uploading the raw CSV to `daily-brew-group-raw-csv`, the Lambda loaded:

- 382 transaction rows
- 1051 transaction item rows

Example CloudWatch log output:

```text
raw_rows_loaded=382
transactions_inserted=382
transaction_items_inserted=1051
lambda_handler: finished
```

## Useful Redshift Queries

Check row counts:

```sql
SELECT COUNT(*) AS transaction_count
FROM daily_brew_group.transactions;

SELECT COUNT(*) AS transaction_item_count
FROM daily_brew_group.transaction_items;
```

Total sales:

```sql
SELECT SUM(total_amount) AS total_sales
FROM daily_brew_group.transactions;
```

Sales by payment method:

```sql
SELECT payment_method, SUM(total_amount) AS total_sales
FROM daily_brew_group.transactions
GROUP BY payment_method
ORDER BY total_sales DESC;
```

Best-selling items:

```sql
SELECT item_name, COUNT(*) AS times_sold
FROM daily_brew_group.transaction_items
GROUP BY item_name
ORDER BY times_sold DESC;
```

Revenue by item:

```sql
SELECT item_name, SUM(item_price) AS item_revenue
FROM daily_brew_group.transaction_items
GROUP BY item_name
ORDER BY item_revenue DESC;
```

Sales by hour:

```sql
SELECT EXTRACT(hour FROM transaction_time) AS hour_of_day,
       SUM(total_amount) AS total_sales
FROM daily_brew_group.transactions
GROUP BY hour_of_day
ORDER BY hour_of_day;
```

## Sprint 3 Grafana

Sprint 3 adds dashboards using Grafana.

The dashboard flow is:

```text
Redshift + CloudWatch
-> Grafana running on EC2
-> sales and infrastructure dashboards
```

AWS resources:

- CloudFormation stack: `daily-brew-group-grafana-stack`
- EC2 instance: `daily-brew-group-grafana-ec2`
- Grafana URL: `http://34.250.20.142`

Grafana data sources:

- `Daily Brew Redshift`
  - Uses the PostgreSQL data source to query Redshift.
  - Reads sales data from `daily_brew_group.transactions` and `daily_brew_group.transaction_items`.
- `CloudWatch`
  - Reads AWS metrics for Lambda and EC2 monitoring.

Grafana dashboards:

- `Daily Brew Sales Dashboard`
  - Total revenue
  - Total transactions
  - Best-selling products
  - Revenue by hour
  - Revenue by branch
  - Products sold per branch
- `Daily Brew Infrastructure Monitoring`
  - Lambda invocations
  - Lambda errors
  - Lambda duration
  - Grafana EC2 CPU utilization

Dashboard JSON backups are saved in:

```text
aws/grafana/dashboards/
```

## Sensitive Data

The raw CSV contains sensitive customer information.

The ETL process does not store:

- customer name
- card number

Only cleaned transaction and item data is stored in PostgreSQL or Redshift.
