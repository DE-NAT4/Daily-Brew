 def lambda_handler(event, context):
        cfg = get_config()

        CLUSTER_ID = "redshiftcluster-zzvcloxeu2tl"
        DATABASE = cfg['database-name']
        DB_USER = cfg['user']

        db.create_db(DATABASE, DB_USER)
