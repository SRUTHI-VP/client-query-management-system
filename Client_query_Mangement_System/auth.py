import hashlib
import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="your username",         
        password="your password", 
        database="your database name"
    )


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_pw = hash_password(password)

    cursor.execute("""
        SELECT role FROM users
        WHERE username = %s AND hashed_password = %s
    """, (username, hashed_pw))

    result = cursor.fetchone()
    conn.close()

 
    return result[0] if result else None

