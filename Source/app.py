import psycopg2
from dotenv import load_dotenv
import os
import utils
import db

transaction_list = utils.export()

db.db_import(transaction_list)