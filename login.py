import streamlit as st
import mysql.connector

# Function to create a connection to MySQL
def create_connection():
    connection = mysql.connector.connect(
        host="localhost",           # XAMPP MySQL server host (localhost)
        user="root",                # MySQL user (default for XAMPP is root)
        password="",                # MySQL password (default for XAMPP is empty)
        database="costruction"    # Name of the database you created in phpMyAdmin
    )
    return connection

# Function to authenticate user
def authenticate_user(username, password, role):
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT username, role FROM login WHERE username = %s AND password = %s AND role = %s",
        (username, password, role)
    )
    user = cursor.fetchone()
    
    cursor.close()
    connection.close()
    return user

# Function to redirect based on role
def redirect_url(role):
    if role == "admin":
        st.markdown('<meta http-equiv="refresh" content="0; url=http://localhost:8502/">', unsafe_allow_html=True)
    elif role == "supervisor":
        st.markdown('<meta http-equiv="refresh" content="0; url=http://localhost:8503/">', unsafe_allow_html=True)

# Streamlit Interface
st.title("Login Page")

# Input fields for login
username = st.text_input("Username")
password = st.text_input("Password", type="password")  # Mask password input
role = st.selectbox("Role", options=["admin", "supervisor"])  # Dropdown for role selection

# Login button
if st.button("Login"):
    user = authenticate_user(username, password, role)
    if user:
        st.success(f"Welcome, {user['username']}! Redirecting as a {user['role']}...")
        redirect_url(user["role"])
    else:
        st.error("Invalid username, password, or role.")
