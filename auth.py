import uuid
from database import get_connection
from utils.security import hash_password, verify_password

def create_user(name, email, password):
    conn = get_connection()
    cursor = conn.cursor()

    hashed = hash_password(password)

    cursor.execute("""
    INSERT INTO users (uuid, name, email, password)
    VALUES (?, ?, ?, ?)
    """, (str(uuid.uuid4()), name, email, hashed))

    conn.commit()
    conn.close()

def authenticate_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cursor.fetchone()

    conn.close()

    if user and verify_password(password, user["password"]):
        return user

    return None