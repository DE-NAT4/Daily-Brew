import boto3
import time

redshift_data = boto3.client('redshift-data')

CLUSTER_ID = "redshiftcluster-zzvcloxeu2tl"
#DATABASE = "your_database"
#DB_USER = "your_db_user"


def run_sql(sql, dbusername, DATABASE):
    """Run a single SQL statement"""
    response = redshift_data.execute_statement(
        ClusterIdentifier=CLUSTER_ID,
        Database=DATABASE,
        DbUser=dbusername,
        Sql=sql
    )
    return response["Id"]


def wait_for_statement(statement_id):
    while True:
        result = redshift_data.describe_statement(Id=statement_id)
        status = result["Status"]

        if status in ["FINISHED", "FAILED", "ABORTED"]:
            if status != "FINISHED":
                raise Exception(f"SQL failed: {result['Error']}")
            return

        time.sleep(1)

def createdb(dbname, dbuser):
    statements = [

        """
        DROP TABLE IF EXISTS couriers;
        """,

        """
        CREATE TABLE public.couriers (
            courier_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            name varchar(100),
            phone varchar(30)
        );
        """

        """
        DROP TABLE IF EXISTS order_items;
        """,

        """
        CREATE TABLE public.order_items (
            order_id integer NOT NULL,
            product_id integer NOT NULL,
            quantity integer DEFAULT 1 NOT NULL,
            PRIMARY KEY (order_id, product_id)
        );
        """,

        """
        DROP TABLE IF EXISTS order_status;
        """,

        """
        CREATE TABLE public.order_status (
            status_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            status_name varchar(50)
        );
        """,

        """
        DROP TABLE IF EXISTS orders;
        """,

        """
        CREATE TABLE public.orders (
            order_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            customer_name varchar(100),
            customer_address varchar(100),
            customer_phone varchar(20),
            courier_id integer,
            status_id integer
        );
        """,

        """
        DROP TABLE IF EXISTS products;
        """,

        """
        CREATE TABLE public.products (
            product_id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            name varchar(100),
            price numeric(10,2),
            quantity integer DEFAULT 0 NOT NULL
        );
        """,

        """
        ALTER TABLE order_items
        ADD CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE;
        """,

        """
        ALTER TABLE order_items
        ADD CONSTRAINT fk_order_items_product
        FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE;
        """,

        """
        ALTER TABLE orders
        ADD CONSTRAINT fk_orders_courier
        FOREIGN KEY (courier_id) REFERENCES couriers(courier_id);
        """,

        """
        ALTER TABLE orders
        ADD CONSTRAINT fk_orders_status
        FOREIGN KEY (status_id) REFERENCES order_status(status_id);
        """
    ]

    for sql in statements:
        print("Running:", sql.strip()[:60])

        stmt_id = run_sql(sql, dbuser, dbname)

        # optional: wait for completion
        wait_for_statement(stmt_id)
