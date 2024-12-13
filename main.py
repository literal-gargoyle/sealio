from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
from difflib import SequenceMatcher
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for sessions
users_db_file = 'users.json'

# Function to calculate similarity between hashtags
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Load users from JSON file
def load_users_from_json():
    try:
        with open(users_db_file, 'r') as f:
            data = json.load(f)
            return data.get("users", [])
    except FileNotFoundError:
        return []  # If the file doesn't exist, return an empty list

# Save users to JSON file
def save_users_to_json(users):
    with open(users_db_file, 'w') as f:
        json.dump({"users": users}, f, indent=4)

# Add a new user
def add_user(username, password, liked_hashtags):
    # Hash the password before saving it
    hashed_password = generate_password_hash(password)
    users = load_users_from_json()
    users.append({"username": "@" + username, "password": hashed_password, "liked_hashtags": liked_hashtags})
    save_users_to_json(users)

# Check if user exists (authentication)
def authenticate(username, password):
    users = load_users_from_json()
    user = next((u for u in users if u['username'] == username), None)
    if user and check_password_hash(user['password'], password):  # Verify hashed password
        return True
    return False

# Route to handle signup
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get('username')  # Changed from handle to username
    password = data.get('password')
    liked_hashtags = data.get('liked_hashtags', [])

    # Check if username already exists
    users = load_users_from_json()
    if any(user['username'] == username for user in users):
        return jsonify({"success": False, "message": "Username already exists"})
    
    # Add user to the users file
    add_user(username, password, liked_hashtags)
    
    return jsonify({"success": True, "message": "User created successfully"})

# Route to handle login
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get('username')  # Changed from handle to username
    password = data.get('password')

    # Authenticate user by username and password
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
