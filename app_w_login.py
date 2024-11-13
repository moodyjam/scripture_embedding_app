import streamlit as st
import sqlite3
import bcrypt
import base64
import pandas as pd
import numpy as np
import openai
import os
from app import main_app

# ========================================
# Set Page Configuration
# ========================================
st.set_page_config(page_title="Scripture Embedding Search", page_icon="📖", layout="wide")

# ========================================
# Initialize Session State Variables
# ========================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''

# ========================================
# Database Setup
# ========================================
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ========================================
# Password Handling Functions
# ========================================
def hash_password(password):
    """
    Hash a plaintext password using bcrypt.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed):
    """
    Verify a plaintext password against the hashed version.
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

# ========================================
# User Management Functions
# ========================================
def add_user(username, password):
    """
    Add a new user to the database with a hashed password.
    Returns True if successful, False if username already exists.
    """
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    hashed = hash_password(password)  # This is bytes
    hashed_b64 = base64.b64encode(hashed).decode('utf-8')  # Convert bytes to base64 string
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username.strip(), hashed_b64))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()

def authenticate_user(username, password):
    """
    Authenticate a user by verifying the provided password.
    Returns True if authentication is successful, False otherwise.
    """
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username = ?', (username.strip(),))
    result = c.fetchone()
    conn.close()
    if result:
        hashed_b64 = result[0]  # Retrieve base64 string from database
        try:
            hashed = base64.b64decode(hashed_b64)  # Convert base64 string back to bytes
        except base64.binascii.Error:
            return False
        return verify_password(password, hashed)
    else:
        return False

# ========================================
# Callback Functions for Login and Registration
# ========================================
def process_login():
    """
    Process the login attempt.
    Sets 'logged_in' and 'username' in session state upon success.
    Sets 'login_error' in session state upon failure.
    """
    username = st.session_state['login_username']
    password = st.session_state['login_password']
    
    if authenticate_user(username, password):
        st.session_state['logged_in'] = True
        st.session_state['username'] = username.strip()
        # Clear any previous error messages
        st.session_state['login_error'] = ""
    else:
        st.session_state['login_error'] = "Invalid username or password"

def process_registration():
    """
    Process the registration attempt.
    Sets 'register_success' and clears 'register_error' upon success.
    Sets 'register_error' upon failure.
    """
    username = st.session_state['register_username']
    password = st.session_state['register_password']
    confirm_password = st.session_state['register_confirm_password']
    
    if password != confirm_password:
        st.session_state['register_error'] = "Passwords do not match"
        st.session_state['register_success'] = ""
    else:
        success = add_user(username, password)
        if success:
            st.session_state['register_success'] = "Account created successfully! Please log in."
            st.session_state['register_error'] = ""
        else:
            st.session_state['register_error'] = "Username already exists"
            st.session_state['register_success'] = ""

# ========================================
# UI Components for Login and Registration
# ========================================
def login():
    """
    Render the login UI.
    """
    st.title("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    st.button("Login", on_click=process_login, key="login_button")
    
    # Display error message if present
    if 'login_error' in st.session_state and st.session_state['login_error']:
        st.error(st.session_state['login_error'])

def register():
    """
    Render the registration UI.
    """
    st.title("Create an Account")
    username = st.text_input("Choose a Username", key="register_username")
    password = st.text_input("Choose a Password", type="password", key="register_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm_password")
    st.button("Register", on_click=process_registration, key="register_button")
    
    # Display error or success messages
    if 'register_error' in st.session_state and st.session_state['register_error']:
        st.error(st.session_state['register_error'])
    if 'register_success' in st.session_state and st.session_state['register_success']:
        st.success(st.session_state['register_success'])

# ========================================
# Navigation Between Login/Register and Main App
# ========================================
def login_or_register():
    """
    Allow users to navigate between login and registration.
    """
    option = st.sidebar.selectbox("Menu", ["Login", "Register"])
    if option == "Login":
        login()
    else:
        register()

# ========================================
# Run the Streamlit App
# ========================================
def run_app():
    """
    Determine which UI to display based on the user's login state.
    """
    if st.session_state['logged_in']:
        main_app()
    else:
        login_or_register()

run_app()