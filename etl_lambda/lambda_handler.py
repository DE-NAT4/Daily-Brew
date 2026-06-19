import boto3
import json
import logging
import time
import db

ssm = boto3.client("ssm")
PARAM_NAME = "daily_brew_redshift_settings"

def get_config():
    resp = ssm.get_parameter(Name=PARAM_NAME, WithDecryption=True)
    print("got config")
    return json.loads(resp["Parameter"]["Value"])

def lambda_handler(event, context):

       cfg = get_config()

       CLUSTER_ID = "redshiftcluster-zzvcloxeu2tl"
       DATABASE = cfg['database-name']
       DB_USER = cfg['user']

       db.createdb(DATABASE, DB_USER)
