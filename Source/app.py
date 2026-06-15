import psycopg2
from dotenv import load_dotenv
import os
import utils
import db

transaction_list = utils.export()

conn = db.db_open()
db.db_import(conn, transaction_list)