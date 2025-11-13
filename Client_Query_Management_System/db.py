import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",           
        user="enter your username",        
        password="enter your password",
        database="enter your database name"
    )