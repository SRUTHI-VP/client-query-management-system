import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="your username",         
        password="your password", 
        database="your database name"
    )
