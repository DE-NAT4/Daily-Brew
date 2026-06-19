import boto3
import json
import logging
import time
 
logger = logging.getLogger()

logger.info("start")
print("print start")

ssm = boto3.client("ssm")
# 1. Initialize the native Redshift Data client
redshift_data = boto3.client("redshift-data")
 
PARAM_NAME = "daily_brew_redshift_settings"

def get_config():
    resp = ssm.get_parameter(Name=PARAM_NAME, WithDecryption=True)
    print("got config")
    return json.loads(resp["Parameter"]["Value"])
 
def lambda_handler(event, context):

################
    for record in event['Records']:

        bucket = record['s3']['bucket']['name']

        # S3 keys are URL encoded
        key = urllib.parse.unquote_plus(record['s3']['object']['key'])

        print(f"New file detected: s3://{bucket}/{key}")

        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')

        csv_reader = csv.DictReader(io.StringIO(content))

        for row in csv_reader:
            print(row)  # process each row here

###############

    print("lambda_handler start")
    cfg = get_config()
    # 2. Execute the query using the native AWS API client
    print(f"database name: {cfg['database-name']}")
    print(f"dbuser: {cfg['user']}")

    response = redshift_data.execute_statement(
    ClusterIdentifier="redshiftcluster-zzvcloxeu2tl",
    Database=cfg["database-name"],
    DbUser=cfg["user"],
    Sql="""
        SELECT schemaname, tablename
        FROM pg_tables
        WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
        ORDER BY schemaname, tablename;
    """
)

#SELECT * FROM test_lambda_insert
    print("connected")

    statement_id = response["Id"]

    while True:
        desc = redshift_data.describe_statement(Id=statement_id)
        status = desc["Status"]

        if status in ["FINISHED", "FAILED", "ABORTED"]:
            break

        time.sleep(1)

    result = redshift_data.get_statement_result(Id=statement_id)

    #print(f"result: {result['Records']}")
    print(f"result: {result}")
    # 3. Return the Query ID so you can track it
    return {
        "status": "ok",
        "query_id": response["Id"]
    }

