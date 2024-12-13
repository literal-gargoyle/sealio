from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
from difflib import SequenceMatcher
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for sessions

# Dummy user data
users_db = []

# Function to calculate similarity between hashtags
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Load users from JSON (use actual file in a production environment)
def load_users_from_json():
    return users_db  # In-memory storage for simplicity

# Add a new user
def add_user(username, password):
    users_db.append({"username": username, "password": password})

# Check if user exists (authentication)
def authenticate(username, password):
    user = next((u for u in users_db if u['username'] == username), None)
    if user and user['password'] == password:
        return True
    return False

# Route to handle signup
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Check if username already exists
    if any(user['username'] == username for user in users_db):
        return jsonify({"success": False, "message": "Username already exists"})
    
    # Add user to the in-memory database
    add_user(username, password)
    
    return jsonify({"success": True, "message": "User created successfully"})

# Route to handle login
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Authenticate user
    if authenticate(username, password):
        session['username'] = username  # Store username in session
        return jsonify({"success": True, "message": "Logged in successfully"})
    else:
        return jsonify({"success": False, "message": "Invalid username or password"})

# Route for the home page (after login)
@app.route("/home")
def home():
    if 'username' in session:
        # Display posts, or other content for logged-in users
        return render_template("home.html", username=session['username'])
    return redirect(url_for("index"))

# Route to log out
@app.route("/logout")
def logout():
    session.pop('username', None)  # Remove username from session
    return redirect(url_for("index"))

# Main route to display the login/signup page
@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
