import sqlite3
from sqlite3 import Error
import threading
import hashlib
import os

class Database:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.connection = None
        return cls._instance

    def __init__(self):
        if not self.connection:
            try:
                self.connection = sqlite3.connect('secure_file_system.db', check_same_thread=False)
                self.create_tables()
            except Error as e:
                print(f"Database error: {e}")

    def create_tables(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    verified BOOLEAN DEFAULT 0
                )
            ''')
            self.connection.commit()
        except Error as e:
            print(f"Error creating tables: {e}")
        finally:
            cursor.close()

    def add_user(self, username, email, password):
        with self._lock:
            try:
                cursor = self.connection.cursor()
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                             (username, email, hashed_password))
                self.connection.commit()
                return True
            except Error as e:
                print(f"Error adding user: {e}")
                return False
            finally:
                cursor.close()

    def verify_user(self, email):
        with self._lock:
            try:
                cursor = self.connection.cursor()
                cursor.execute('UPDATE users SET verified = 1 WHERE email = ?', (email,))
                self.connection.commit()
                return True
            except Error as e:
                print(f"Error verifying user: {e}")
                return False
            finally:
                cursor.close()

    def check_login(self, email, password):
        with self._lock:
            try:
                cursor = self.connection.cursor()
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?',
                             (email, hashed_password))
                user = cursor.fetchone()
                return user is not None
            except Error as e:
                print(f"Error checking login: {e}")
                return False
            finally:
                cursor.close()

    def update_password(self, email, new_password):
        with self._lock:
            try:
                cursor = self.connection.cursor()
                hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
                cursor.execute('UPDATE users SET password = ? WHERE email = ?',
                             (hashed_password, email))
                self.connection.commit()
                return True
            except Error as e:
                print(f"Error updating password: {e}")
                return False
            finally:
                cursor.close()

    def __del__(self):
        if self.connection:
            self.connection.close() 