"""
This is the backend of the web application
"""
import os
import logging
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session, url_for, redirect
from flask_cors import CORS
import requests
from flask_session import Session
from requests.exceptions import RequestException
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")
CORS(app)
logging.basicConfig(level=logging.INFO)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Connect to MongoDB
try:
    client = MongoClient("database", 27017)
    db = client["database"]
    collection = db["chat"]
    user_collection = db["users"]
    
    # Ensure collections exist (MongoDB creates them automatically, but this makes it explicit)
    if "chat" not in db.list_collection_names():
        db.create_collection("chat")
        logging.info("Created 'chat' collection")
    
    if "users" not in db.list_collection_names():
        db.create_collection("users")
        logging.info("Created 'users' collection")
    
    logging.info("Database connection established successfully")
    logging.info(f"Available collections: {db.list_collection_names()}")
    
except Exception as e:
    logging.error(f"Database connection error: {e}")
    print(e)

# def get_db_client(use_mock_db=False):
#     if use_mock_db:
#         return mongomock.MongoClient()

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Render index page.
    """
    if "messages" not in session:
        session["messages"] = {}

    if "user_id" not in session:
        return render_template("login.html")

    else:
        current_personality = session.get("current_personality", "default_personality")
        if request.method == "POST":
            user_input = request.form.get("user_input")
            user_id = session.get("user_id")
            if current_personality not in session["messages"]:
                session["messages"][current_personality] = []

            session["messages"][current_personality].append(
                {"type": "User", "content": user_input}
            )
            logging.info(user_id)
            return render_template(
                "index.html",
                messages=session["messages"][current_personality],
                user_id=user_id,
            )

        messages = session["messages"].get(current_personality, [])
        return render_template(
            "index.html", messages=messages, user_id=session.get("user_id")
        )


@app.route("/get_response", methods=["POST"])
def get_response():
    """
    Get response for user input.
    """
    user_input = request.form.get("user_input")
    personality = request.form.get("personality", "helpful")
    user_id = session["user_id"]
    session[
        "current_personality"
    ] = personality  # Save the current personality in session

    logging.info("get_response: " + user_id)
    try:
        response = requests.post(
            "http://client:5002/get_response",
            json={"prompt": user_input, "personality": personality, "user_id": user_id},
            timeout=60,
        )
        response.raise_for_status()
        ai_response = response.json().get("response")
        if "messages" not in session:
            session["messages"] = {}
        if personality not in session["messages"]:
            session["messages"][personality] = []

        session["messages"][personality].append(
            {"type": "Assistant", "content": ai_response}
        )
        return jsonify(ai_response)
    except RequestException as e:
        logging.error("Error making the request to the client: %s", str(e))
        return (
            jsonify(
                {
                    "error": "An error occurred while getting the response from the client"
                }
            ),
            500,
        )


@app.route("/load_chats", methods=["GET"])
def load_chats():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user_chats = {}
    chat_records = collection.find({"conversation_key": {"$regex": f"^{user_id}_"}})

    for record in chat_records:
        personality = record["conversation_key"].split("_")[1]
        user_chats[personality] = []
        for message in record["history"]:
            # Format the message for the frontend
            msg_type = "user" if message["type"] == "User" else "ai"
            user_chats[personality].append(
                {"type": msg_type, "content": message["content"]}
            )

    return jsonify(user_chats)


@app.route("/clear_chats", methods=["POST"])
def clear_chats():
    user_id = request.form.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    # Clear all chats associated with the user_id
    result = collection.delete_many({"conversation_key": {"$regex": f"^{user_id}_"}})
    if result.deleted_count > 0:
        return jsonify({"status": "success"})
    else:
        return jsonify({"error": "Failed to clear chats"}), 500


@app.route("/clear_session", methods=["POST"])
def clear_session():
    """
    Route for clearing session.
    """
    try:
        session.clear()
        return jsonify({"message": "Session cleared successfully"})
    except RuntimeError as e:
        logging.error("Error clearing session: %s", str(e))
        return jsonify({"error": "An error occurred while clearing the session"}), 500


# Login, Sign Up Functionality
@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Renders the signup page"""
    # If there is a user_id in session, it redirects them back to the home page
    if "user_id" in session:
        return redirect(url_for("index"))

    # Check if database is connected
    if user_collection is None:
        return render_template("signup.html", errors=["Database connection error. Please try again later."])

    # If there is no account, then we allow the user to create one.
    if request.method == "POST":
        try:
            # We allow the user to create their username, password, confirm password, email
            username = request.form["username"]
            password = request.form["password"]
            confirm_password = request.form["confirm_password"]
            email = request.form["email"]
            errors = []

            # This checks if there is already a user that has this exact username
            if user_collection.find_one({"username": username}):
                errors.append("Username already exists!")
                logging.info("Username already exists error")

            # This checks if there is already a user that has this exact email
            elif user_collection.find_one({"email": email}):
                errors.append("Email already used, try another or try logging in!")
                logging.info("Email already exists error")

            # This checks if the password is in between 8-20 characters
            elif not 8 <= len(password) <= 20:
                errors.append("Password must be between 8 and 20 characters long!")
                logging.info("Password length error")

            # This checks if the password does not have any numbers
            elif not any(char.isdigit() for char in password):
                errors.append("Password should have at least one number!")
                logging.info("Password missing number error")

            # This checks if the password does not have any alphabets
            elif not any(char.isalpha() for char in password):
                errors.append("Password should have at least one alphabet!")
                logging.info("Password missing letter error")

            # This checks if the password and the confirm password do not match
            elif not confirm_password == password:
                errors.append("Passwords do not match!")
                logging.info("Password mismatch error")

            # If any errors, it will re-render the signup.html page and allow the user to try again
            if errors:
                logging.info(f"Signup failed with errors: {errors}")
                return render_template("signup.html", errors=errors)

            # If user managed to create a proper account, it will generate a hash for their password
            password_hash = generate_password_hash(password)

            # Here we insert their account details to the database
            result = user_collection.insert_one(
                {
                    "username": username,
                    "password": password_hash,
                    "email": email,
                }
            )
            
            logging.info(f"User created successfully with ID: {result.inserted_id}")

            # This redirects the user to the login page where they must login to access the webpage.
            return redirect(url_for("login"))
            
        except Exception as e:
            logging.error(f"Error during signup: {e}")
            return render_template("signup.html", errors=["An error occurred during signup. Please try again."])

    # Renders the signup.html page
    return render_template("signup.html")


# Rendering either the login template if they haven't logged in, otherwise, the home page
@app.route("/login", methods=["GET"])
def login():
    """Renders the login page"""
    if "user_id" in session:
        return redirect(url_for("index"))
    return render_template("login.html")


# This function is the backend of the login functionality from the login.html file
@app.route("/login_auth", methods=["POST"])
def login_auth():
    """Route for login authentication"""
    # If a user is already logged in, redirect them to the home page
    if "user_id" in session:
        return redirect(url_for("index"))

    # Check if database is connected
    if user_collection is None:
        return render_template("login.html", errors=["Database connection error. Please try again later."])

    # Else, ask them to login by inputting a username and password
    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]
            session["username"] = username

            errors = []

            # Once inputted their username and password, check the database for existing users
            user = user_collection.find_one({"username": username})

            # We provide the _id attribute of the user to the user_id in the session
            if user and check_password_hash(user["password"], password):
                # User sessions to keep track of who's logged in
                session["user_id"] = str(user["_id"])
                return redirect(url_for("index"))

            # If the username or password does not match we render the login.html template once more
            errors.append("Invalid username or password!")
            return render_template("login.html", errors=errors)
        except Exception as e:
            logging.error(f"Error during login: {e}")
            return render_template("login.html", errors=["An error occurred during login. Please try again."])
    return render_template("login.html", errors=["Invalid request method"])


@app.route('/forgot_password', methods = ['GET','POST'])
def forgot_password():
    if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            email = request.form['email']
            errors = []
            user = user_collection.find_one({'email': email, 'username':username})

            if not user:
                errors.append("Invalid username or email!")
            
            elif len(password) < 8 & len(password) > 20:
                errors.append("Password must be between 8 and 20 characters long!")
            
            elif not any(char.isdigit() for char in password):
                errors.append("Password should have at least one number!")
            
            elif not any(char.isalpha() for char in password):
                errors.append("Password should have at least one alphabet!")
            
            elif not confirm_password == password:
                errors.append("Passwords do not match!")

            if errors:
                return render_template('forgot_password.html', errors=errors)
            
            else:
                password_hash = generate_password_hash(password)
                filter = {'email': email, 'username':username}      
                update = {'$set': {'password': password_hash}}
                user_collection.update_one(filter, update)                   
                return redirect(url_for('login'))
            
    return render_template('forgot_password.html')


# Here we have another route, if the user decides to logout,
# it will pop their user_id from the session and redirect them to the login page
@app.route("/logout")
def logout():
    """route for logout"""
    session.pop("user_id", None)
    clear_session()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
