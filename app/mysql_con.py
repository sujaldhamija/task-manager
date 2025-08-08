import mysql.connector, os
from dotenv import load_dotenv

load_dotenv()

db_config = {
    "host": os.getenv("host"),
    "user": os.getenv("user"),
    "password": os.getenv("password"),
    "db": os.getenv("db"),
}

mydb = mysql.connector.connect(**db_config)

mycursor = mydb.cursor(dictionary=True)
