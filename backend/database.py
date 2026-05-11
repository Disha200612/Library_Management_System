import mysql.connector

def get_db_connection():

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Disha@123",
        database="library2_db"
    )

    return conn