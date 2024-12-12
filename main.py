from flask import Flask, render_template, request, redirect, url_for
import json
from difflib import SequenceMatcher
import random

app = Flask(__name__)

# Function to calculate similarity between hashtags
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Recommend posts based on user preferences and engagement potential
def recommend_posts(user_liked_hashtags, posts, threshold=0.3):
    recommendations = []
    
    for post in posts:
        score = 0
        
        # Calculate relevance score based on hashtag similarity
        for hashtag in post["hashtags"]:
            for liked_hashtag in user_liked_hashtags:
                score += similar(hashtag, liked_hashtag)
        
        # Increase score for popular topics (like machine learning or Python)
        popular_topics = ["#python", "#machinelearning", "#AI", "#webdevelopment"]
        for hashtag in post["hashtags"]:
            if hashtag in popular_topics:
                score += 0.5  # Add more weight for popular topics
        
        # Adjust score for engagement potential (e.g., tips, tutorials)
        if "tips" in post["content"] or "guide" in post["content"]:
            score += 0.4
        
        # Random factor for engagement, simulating real user interest
        score += random.uniform(0.1, 0.3)
        
        # Only consider posts that pass a minimum threshold for similarity
        if score > threshold:
            recommendations.append((post["content"], score))
    
    # Sort recommendations based on score
    recommendations.sort(key=lambda x: x[1], reverse=True)
    return recommendations

# Load users and posts from their respective JSON files
def load_users_from_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data["users"]

def load_posts_from_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data["posts"]

# Find a user's liked hashtags by their handle
def get_user_liked_hashtags(users, handle):
    for user in users:
        if user["handle"] == handle:
            return user["liked_hashtags"]
    return []

# Add a hashtag to the user's liked hashtags
def update_user_likes(users, handle, post_hashtags):
    for user in users:
        if user["handle"] == handle:
            for hashtag in post_hashtags:
                if hashtag not in user["liked_hashtags"]:
                    user["liked_hashtags"].append(hashtag)
    return users

# Save updated user data back to JSON file
def save_users_to_json(users, filename="users.json"):
    with open(filename, 'w') as file:
        json.dump({"users": users}, file, indent=4)

# Main route to display form and recommendations
@app.route("/", methods=["GET", "POST"])
def index():
    recommended = []
    if request.method == "POST":
        user_handle = request.form["handle"]
        users = load_users_from_json("users.json")
        posts = load_posts_from_json("posts.json")

        user_liked_hashtags = get_user_liked_hashtags(users, user_handle)
        if user_liked_hashtags:
            recommended = recommend_posts(user_liked_hashtags, posts)
        else:
            recommended = [("No recommendations found for this user.", 0)]
    
    return render_template("index.html", recommendations=recommended)

# Route to handle liking a post
@app.route("/like_post", methods=["POST"])
def like_post():
    user_handle = request.form["handle"]
    post_id = int(request.form["post_id"])
    
    # Load posts and users
    users = load_users_from_json("users.json")
    posts = load_posts_from_json("posts.json")
    
    # Get the hashtags of the liked post
    liked_post = next((post for post in posts if post["id"] == post_id), None)
    if liked_post:
        hashtags = liked_post["hashtags"]
        # Update the user's liked hashtags
        users = update_user_likes(users, user_handle, hashtags)
        save_users_to_json(users)  # Save updated users data
    
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
