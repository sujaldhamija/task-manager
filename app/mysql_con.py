import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    db="to-do-list-python",
    autocommit=True
)

mycursor = mydb.cursor(dictionary=True)
