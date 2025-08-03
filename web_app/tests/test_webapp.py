"""Module for Testing Python Functions"""
from unittest.mock import MagicMock, patch
import pytest
from bson import ObjectId
from werkzeug.security import generate_password_hash
from requests.exceptions import RequestException
from web_app.app import app
from flask import url_for
# from web_app.app import get_db_client
# import mongomock
# import pymongo

@pytest.fixture
def mock_db(monkeypatch):
    mock_collection = MagicMock()
    monkeypatch.setattr('client.client.collection', mock_collection) 
    return mock_collection

class Tests:
    """Test Functions for the Web App"""

    mock_user_id = str(ObjectId())
    
    # @pytest.fixture(scope="function")
    # def mock_db(self):
    #     mock_db = get_db_client(use_mock_db=True)
    #     yield mock_db

    # Test functions
    def test_sanity_check(self):
        """Run a simple test for the webapp side that always passes."""
        actual = True
        expected = True
        assert actual == expected, "Expected True to be equal to True!"

    @pytest.fixture
    def client(self):
        """Test client for web app"""
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_index_route(self, client):
        """Test index route"""
        response = client.get("/")
        assert response.status_code == 200

    def test_login_user_logged_in(self, client):
        """Test login route when user is logged in."""
        with client.session_transaction() as session:
            session["user_id"] = "some_user_id"

        response = client.get("/login")

        assert response.status_code == 302
        assert "/" in response.headers["Location"]

    def test_login_user_not_logged_in(self, client):
        """Test login route when user is not logged in."""
        with client.session_transaction() as session:
            session.pop("user_id", None)

        response = client.get("/login")
        assert response.status_code == 200

    def test_logout(self, client):
        """Test logout"""
        with client.session_transaction() as session:
            session["user_id"] = 123 

        response = client.get("/logout")

        with client.session_transaction() as session:
            assert "user_id" not in session

        assert response.status_code == 302  
    
    @patch('web_app.app.requests.post')
    def test_get_response_valid_data(self, mock_post, client):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "mocked response"}
        mock_post.return_value = mock_response

        with client.session_transaction() as session:
            session["user_id"] = self.mock_user_id

        response = client.post("/get_response", data={
            "user_input": "Hello",
            "personality": "Helpful Mom",
            "user_id": ObjectId(),
        })

        assert response.status_code == 200
        assert "response" in response.json
    
    def test_get_response_invalid_data(self, client):
        with client.session_transaction() as session:
            session["user_id"] = self.mock_user_id

        response = client.post("/get_response", data={})

        assert response.status_code == 500 
    
    @patch('web_app.app.requests.post')
    def test_get_response_timeout(self, mock_post, client):
        with client.session_transaction() as session:
            session["user_id"] = self.mock_user_id

        mock_post.side_effect = RequestException("Timeout occurred")
        response = client.post("/get_response", data={"user_input": "Hello"})

        assert response.status_code == 500
        assert "error" in response.json

    @patch('web_app.app.collection.find')
    def test_load_chats_with_valid_user_id(self, mock_find, client):
        """Test load chats route with valid user ID."""
        mock_find.return_value = []
        response = client.get("/load_chats?user_id=" + self.mock_user_id)

        assert response.status_code == 200
        assert isinstance(response.json, dict)
    
    def test_load_chats_without_user_id(self, client):
        response = client.get("/load_chats")

        assert response.status_code == 400
        assert "error" in response.json
    
    @patch('web_app.app.collection.delete_many')
    def test_clear_chats_no_chats_to_delete(self, mock_delete, client):
        """Test clear chats with valid user ID but no chats to delete."""
        mock_delete.return_value.deleted_count = 0
        response = client.post("/clear_chats", data={"user_id": self.mock_user_id})

        assert response.status_code == 500
        assert response.json.get("error") == "Failed to clear chats"

    @patch('web_app.app.collection.delete_many')
    def test_clear_chats_valid_user_id(self, mock_delete, client):
        mock_delete.return_value.deleted_count = 1
        response = client.post("/clear_chats", data={"user_id": self.mock_user_id})

        assert response.status_code == 200
        assert response.json.get("status") == "success"
    
    def test_clear_chats_without_user_id(self, client):
        response = client.post("/clear_chats")

        assert response.status_code == 400
        assert "error" in response.json
    
    def test_clear_session(self, client):
        with client.session_transaction() as session:
            session["user_id"] = self.mock_user_id

        response = client.post("/clear_session")

        assert response.status_code == 200
        assert "message" in response.json
        with client.session_transaction() as session:
            assert "user_id" not in session

    def test_signup_page(self, client):
        """Test that the signup page renders correctly"""
        response = client.get("/signup")
        assert response.status_code == 200
        assert b"Sign Up" in response.data

    @patch('web_app.app.user_collection.insert_one')
    @patch('web_app.app.user_collection.find_one')
    def test_signup_success(self, mock_find_one, mock_insert_one, client):
        """Test successful user signup."""
        mock_find_one.return_value = None
        mock_insert_one.return_value = None

        new_user = {
            "username": "new_user",
            "password": "Password123",
            "confirm_password": "Password123",
            "email": "new_user@email.com",
        }

        response = client.post("/signup", data=new_user)
        assert response.status_code == 200

    @patch('web_app.app.user_collection.find_one')
    def test_signup_with_existing_username(self, mock_find_one, client):
        """Test signup with an existing username"""
        mock_find_one.return_value = {"username": "existing_user"}

        new_user = {
            "username": "existing_user",
            "password": "Password123",
            "confirm_password": "Password123",
            "email": "exis_user@email.com",
        }

        with client.session_transaction() as session:
            session.pop("user_id", None)

        response = client.post("/signup", data=new_user)

        assert response.status_code == 200
        assert b"Username already exists!" in response.data

    @patch('web_app.app.user_collection.find_one')
    def test_signup_password_too_short(self, mock_find_one, client):
        """Test signup with a password that is too short"""
        data = {
            "username": "user",
            "password": "Zx25",
            "confirm_password": "Zx25",
            "email": "user@email.com",
        }
        mock_find_one.return_value = None
        response = client.post("/signup", data=data)
        assert response.status_code == 200
        assert b"Password must be between 8 and 20 characters long!" in response.data

    @patch('web_app.app.user_collection.find_one')
    def test_signup_password_too_long(self, mock_find_one, client):
        """Test signup with a password that is too long"""
        data = {
            "username": "user",
            "password": "PasswordPass12345678912345",
            "confirm_password": "PasswordPass12345678912345",
            "email": "user@email.com",
        }
        mock_find_one.return_value = None
        response = client.post("/signup", data=data)
        assert response.status_code == 200
        assert b"Password must be between 8 and 20 characters long!" in response.data

    @patch('web_app.app.user_collection.find_one')
    def test_signup_password_no_digit(self, mock_find_one, client):
        """Test signup with a password that has no digits"""
        data = {
            "username": "user",
            "password": "PassyPass",
            "confirm_password": "PassyPass",
            "email": "user@email.com",
        }
        mock_find_one.return_value = None
        response = client.post("/signup", data=data)
        assert response.status_code == 200
        assert b"Password should have at least one number!" in response.data

    @patch('web_app.app.user_collection.find_one')
    def test_signup_password_no_alphabet(self, mock_find_one, client):
        """Test signup with a password that has no alphabets"""
        data = {
            "username": "user",
            "password": "12345678",
            "confirm_password": "12345678",
            "email": "user@email.com",
        }
        mock_find_one.return_value = None
        response = client.post("/signup", data=data)
        assert response.status_code == 200
        assert b"Password should have at least one alphabet!" in response.data

    @patch('web_app.app.user_collection.find_one')
    def test_login_auth_success(self, mock_find_one, client):
        """Test successful login authentication."""
        test_username = "test_user"
        test_password = "correct_password"

        with patch("web_app.app.db.users.find_one") as mock_find_one, patch(
            "web_app.app.check_password_hash"
        ) as mock_check_password:
            
            mock_find_one.return_value = {
                "_id": ObjectId(),
                "username": test_username,
                "password": generate_password_hash(test_password),
            }
            mock_check_password.return_value = True

            response = client.post(
                "/login_auth",
                data={"username": test_username, "password": test_password},
            )

            assert response.status_code == 302

    @patch('web_app.app.user_collection.find_one')
    def test_login_auth_failure(self, mock_find_one, client):
        """Test login authentication with wrong credentials."""
        test_username = "test_user"
        test_password = "wrong_password"
       
        with patch("web_app.app.db.find_one") as mock_find_one, patch(
            "web_app.app.check_password_hash"
        ) as mock_check_password:
            
            mock_find_one.return_value = {
                "_id": ObjectId(),
                "username": test_username,
                "password": generate_password_hash("correct_password"),
            }
            mock_check_password.return_value = False

            response = client.post(
                "/login_auth",
                data={"username": test_username, "password": test_password},
            )

            assert response.status_code == 200
            assert b"Invalid username or password!" in response.data

    @patch('web_app.app.user_collection.update_one')
    @patch('web_app.app.user_collection.find_one')
    def test_forgot_password_success(self, mock_find_one, mock_update_one, client):
        """Test successful password reset in forgot password."""
        mock_find_one.return_value = {'email': "email@email.com", 'username': "user"}
        mock_update_one.return_value = None

        user = {
            "username": "user",
            "password": "Password123",
            "confirm_password": "Password123",
            "email": "email@email.com",
        }

        response = client.post("/forgot_password", data=user)

        assert response.status_code == 302
        assert url_for("login") in response.headers["Location"]

    @patch('web_app.app.user_collection.find_one')
    def test_forgot_password_invalid_user(self, mock_find_one, client):
        """Test forgot password invalid user"""
        mock_find_one.return_value = None

        new_user = {
            "username": "existing_user",
            "password": "Password123",
            "confirm_password": "Password123",
            "email": "exis_user@email.com",
        }

        response = client.post("/forgot_password", data=new_user)

        assert response.status_code == 200
        assert b"Invalid username or email!" in response.data
        

    # @patch('web_app.app.user_collection.find_one')
    # def test_forgot_password_short_password(self, mock_find_one, client):
    #     """Test forgot password invalid input"""
    #     mock_find_one.return_value = {'email': "email@email.com", 'username': "user"}

    #     user = {
    #         "username": "user",
    #         "password": "Pass1",
    #         "confirm_password": "Pass1",
    #         "email": "email@email.com",
    #     }

    #     response = client.post("/forgot_password", data=user)

    #     assert response.status_code == 200
    #     assert b"Password must be between 8 and 20 characters long!" in response.data

    @patch('web_app.app.user_collection.find_one')
    def test_forgot_password_no_digit(self, mock_find_one, client):
        """Test forgot password invalid input"""
        mock_find_one.return_value = {'email': "email@email.com", 'username': "user"}

        user = {
            "username": "user",
            "password": "Password",
            "confirm_password": "Password",
            "email": "email@email.com",
        }

        response = client.post("/forgot_password", data=user)

        assert response.status_code == 200
        assert b"Password should have at least one number!" in response.data

    @patch('web_app.app.user_collection.find_one')
    def test_forgot_password_no_alpha(self, mock_find_one, client):
        """Test forgot password invalid input"""
        mock_find_one.return_value = {'email': "email@email.com", 'username': "user"}

        user = {
            "username": "user",
            "password": "12345678",
            "confirm_password": "12345678",
            "email": "email@email.com",
        }

        response = client.post("/forgot_password", data=user)

        assert response.status_code == 200
        assert b"Password should have at least one alphabet!" in response.data

    @patch('web_app.app.user_collection.find_one')
    def test_forgot_password_unmatch(self, mock_find_one, client):
        """Test forgot password invalid input"""
        mock_find_one.return_value = {'email': "email@email.com", 'username': "user"}

        user = {
            "username": "user",
            "password": "Password12",
            "confirm_password": "12Password",
            "email": "email@email.com",
        }

        response = client.post("/forgot_password", data=user)

        assert response.status_code == 200
        assert b"Passwords do not match!" in response.data