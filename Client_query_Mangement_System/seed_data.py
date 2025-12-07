
import mysql.connector
import hashlib

# Function to hash passwords using SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Connect to MySQL
conn = mysql.connector.connect(
     host="localhost",
     user="your username",         
     password="your password", 
     database="your database name"
)
cursor = conn.cursor()





# Sample user data: (username, password, role)
users = [
    ("suresh", "suresh123", "Client"),
    ("anita", "anita123", "Support"),
    ("ravi", "ravi123", "Client"),
    ("meena", "meena123", "Support"),
    ("arjun", "arjun123", "Client"),
    ("deepa", "deepa123", "Support"),
    ("kiran", "kiran123", "Client"),
    ("latha", "latha123", "Support"),
    ("vijay", "vijay123", "Client"),
    ("rekha", "rekha123", "Support")
]

# Insert each user with hashed password
for username, password, role in users:
    hashed_pw = hash_password(password)
    cursor.execute("""
        INSERT INTO users (username, hashed_password, role)
        VALUES (%s, %s, %s)
    """, (username, hashed_pw, role))

conn.commit()
conn.close()
print(" 10 users inserted successfully into the 'users' table.")




