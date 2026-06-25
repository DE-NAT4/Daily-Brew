import boto3
import csv
import io
import logging
import time
import uuid
from datetime import datetime
from urllib.parse import unquote_plus


logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")
redshift_client = boto3.client("redshift-data")

REDSHIFT_CLUSTER_ID = "redshiftcluster-28evy6tdoci9"
REDSHIFT_DATABASE = "daily_brew_cafe_db"
REDSHIFT_USER = "daily_brew_user"
REDSHIFT_SCHEMA = "ma_test"


def escape_sql_text(value):
    return str(value).replace("'", "''")


def run_redshift_sql(sql):
    response = redshift_client.execute_statement(
        ClusterIdentifier=REDSHIFT_CLUSTER_ID,
        Database=REDSHIFT_DATABASE,
        DbUser=REDSHIFT_USER,
        Sql=sql
    )

    statement_id = response["Id"]

    while True:
        statement = redshift_client.describe_statement(Id=statement_id)
        status = statement["Status"]

        if status == "FINISHED":
            return

        if status in ["FAILED", "ABORTED"]:
            raise Exception(statement.get("Error", "Redshift statement failed"))

        time.sleep(1)


def insert_rows(table_name, columns, rows, batch_size=100):
    if not rows:
        return

    column_text = ", ".join(columns)

    for start_index in range(0, len(rows), batch_size):
        batch = rows[start_index:start_index + batch_size]
        values = []

        for row in batch:
            row_values = []

            for value in row:
                if value is None:
                    row_values.append("NULL")
                else:
                    row_values.append(f"'{escape_sql_text(value)}'")

            values.append(f"({', '.join(row_values)})")

        sql = f"""
            INSERT INTO {REDSHIFT_SCHEMA}.{table_name} ({column_text})
            VALUES {', '.join(values)};
        """

        run_redshift_sql(sql)


def lambda_handler(event, context):
    logger.info("lambda_handler: starting")

    record = event["Records"][0]

    bucket_name = record["s3"]["bucket"]["name"]
    file_key = unquote_plus(record["s3"]["object"]["key"])

    logger.info(f"bucket_name={bucket_name}")
    logger.info(f"file_key={file_key}")

    response = s3_client.get_object(
        Bucket=bucket_name,
        Key=file_key
    )

    csv_text = response["Body"].read().decode("utf-8")

    csv_file = io.StringIO(csv_text)
    reader = csv.reader(csv_file)

    raw_rows = list(reader)

    transactions = []
    transaction_items = []

    for raw_row in raw_rows:
        transaction_datetime = raw_row[0]
        branch = raw_row[1].lower()
        items = raw_row[3].lower()
        total_amount = raw_row[4]
        payment_method = raw_row[5].lower()

        transaction_id = str(uuid.uuid4())

        parsed_datetime = datetime.strptime(transaction_datetime, "%d/%m/%Y %H:%M")
        transaction_date = parsed_datetime.strftime("%Y-%m-%d")
        transaction_time = parsed_datetime.strftime("%H:%M:%S")

        transactions.append([
            transaction_id,
            branch,
            total_amount,
            payment_method,
            transaction_date,
            transaction_time
        ])

        items_list = items.split(", ")

        for item in items_list:
            item_name, item_price = item.rsplit(" - ", 1)

            transaction_items.append([
                str(uuid.uuid4()),
                transaction_id,
                item_name,
                item_price
            ])

    insert_rows(
        "transactions",
        [
            "transaction_id",
            "branch",
            "total_amount",
            "payment_method",
            "transaction_date",
            "transaction_time"
        ],
        transactions
    )

    insert_rows(
        "transaction_items",
        [
            "transaction_item_id",
            "transaction_id",
            "item_name",
            "item_price"
        ],
        transaction_items
    )

    logger.info(f"raw_rows_loaded={len(raw_rows)}")
    logger.info(f"transactions_inserted={len(transactions)}")
    logger.info(f"transaction_items_inserted={len(transaction_items)}")
    logger.info("lambda_handler: finished")

    return {
        "statusCode": 200,
        "body": f"Inserted {len(transactions)} transactions and {len(transaction_items)} transaction items from {file_key}"
    }
