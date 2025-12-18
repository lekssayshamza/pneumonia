import sqlite3
import hashlib
import os
import base64
from datetime import datetime
from PIL import Image
import io

# Database file path
DB_PATH = "users.db"

def init_db():
    """Initialize the database and create users and predictions tables if they don't exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Predictions/History table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            prediction_label TEXT NOT NULL,
            confidence REAL NOT NULL,
            image_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password):
    """Register a new user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        password_hash = hash_password(password)
        cursor.execute("""
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        """, (username, email, password_hash))
        
        conn.commit()
        conn.close()
        return True, "Registration successful!"
    except sqlite3.IntegrityError as e:
        conn.close()
        if "username" in str(e).lower():
            return False, "Username already exists. Please choose another."
        elif "email" in str(e).lower():
            return False, "Email already registered. Please use another email."
        else:
            return False, "Registration failed. Please try again."
    except Exception as e:
        conn.close()
        return False, f"An error occurred: {str(e)}"

def verify_user(username, password):
    """Verify user credentials"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    password_hash = hash_password(password)
    cursor.execute("""
        SELECT id, username, email FROM users
        WHERE username = ? AND password_hash = ?
    """, (username, password_hash))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return True, {"id": user[0], "username": user[1], "email": user[2]}
    else:
        return False, "Invalid username or password."

def user_exists(username):
    """Check if a username exists"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    exists = cursor.fetchone() is not None
    
    conn.close()
    return exists

def email_exists(email):
    """Check if an email exists"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    exists = cursor.fetchone() is not None
    
    conn.close()
    return exists

def image_to_base64(image):
    """Convert PIL Image to base64 string"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

def base64_to_image(img_str):
    """Convert base64 string to PIL Image"""
    img_data = base64.b64decode(img_str)
    return Image.open(io.BytesIO(img_data))

def save_prediction(user_id, prediction_label, confidence, image):
    """Save a prediction to the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        image_data = image_to_base64(image)
        cursor.execute("""
            INSERT INTO predictions (user_id, prediction_label, confidence, image_data)
            VALUES (?, ?, ?, ?)
        """, (user_id, prediction_label, confidence, image_data))
        
        conn.commit()
        prediction_id = cursor.lastrowid
        conn.close()
        return True, prediction_id
    except Exception as e:
        conn.close()
        return False, f"Error saving prediction: {str(e)}"

def get_user_predictions(user_id, limit=50):
    """Get all predictions for a user, ordered by most recent"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, prediction_label, confidence, image_data, created_at
        FROM predictions
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (user_id, limit))
    
    predictions = cursor.fetchall()
    conn.close()
    
    results = []
    for pred in predictions:
        results.append({
            'id': pred[0],
            'label': pred[1],
            'confidence': pred[2],
            'image': base64_to_image(pred[3]),
            'created_at': pred[4]
        })
    
    return results

def delete_prediction(prediction_id, user_id):
    """Delete a prediction (only if it belongs to the user)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM predictions
        WHERE id = ? AND user_id = ?
    """, (prediction_id, user_id))
    
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return deleted

def get_prediction_count(user_id):
    """Get the total number of predictions for a user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM predictions WHERE user_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    
    conn.close()
    return count

# Initialize database on import
init_db()

