import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../database/photo_data.db')

def create_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT UNIQUE,
            file_name TEXT,
            created_date TEXT,
            tags TEXT,
            faces TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_photo(photo):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO photos (file_path, file_name, created_date, tags, faces)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            photo['file_path'],
            photo['file_name'],
            photo['created_date'],
            photo.get('tags', ''),
            photo.get('faces', '')
        ))
        conn.commit()
    except Exception as e:
        print("Error inserting photo:", e)
    finally:
        conn.close()

def search_photos_by_tag_or_face(keyword):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM photos WHERE tags LIKE ? OR faces LIKE ?
    ''', (f'%{keyword}%', f'%{keyword}%'))
    results = cursor.fetchall()
    conn.close()
    return results
