from dotenv import load_dotenv
import os

load_dotenv()

SQL_SERVER_IP = os.getenv("SQL_SERVER_IP")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

RECEIVER_FOLDER_STORE = os.getenv("RECEIVER_FOLDER_STORE")