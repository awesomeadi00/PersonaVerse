from unittest.mock import MagicMock
import pytest
from ..client import app

@pytest.fixture
def test_client():
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        yield test_client

@pytest.fixture
def mock_db(monkeypatch):
    mock_collection = MagicMock()
    monkeypatch.setattr('client.client.collection', mock_collection) 
    return mock_collection

@pytest.fixture
def mock_openai(monkeypatch):
    mock_openai = MagicMock()
    monkeypatch.setattr('langchain.chat_models.ChatOpenAI', mock_openai)  # Adjust the path
    return mock_openai

class Tests:
    def test_sanity_check(self):
        actual = True
        expected = True
        assert actual == expected, "Expected True to be True!"

    def test_get_response_success(self, test_client, mock_db, mock_openai):
        mock_db.find_one.return_value = {"conversation_key": "key", "history": []}
        mock_openai.return_value = MagicMock(content="Test response")
        response = test_client.post('/get_response', json={"prompt": "Hello", "user_id": "123", "personality": "Helpful Mom"})
        assert response.status_code == 200
        assert "Test response" in response.data.decode()

    def test_get_response_bad_request(self, test_client):
        response = test_client.post('/get_response', json={})
        assert response.status_code == 400

    def test_reset_conversation_success(self, test_client, mock_db):
        response = test_client.post('/reset_conversation', json={"user_id": "123"})
        assert response.status_code == 200
        mock_db.delete_many.assert_called_once()

    def test_reset_conversation_bad_request(self, test_client):
        response = test_client.post('/reset_conversation', json={})
        assert response.status_code == 400

    def test_get_response_invalid_personality(self, test_client, mock_db, mock_openai):
        response = test_client.post('/get_response', json={"prompt": "Hello", "user_id": "123", "personality": "Invalid"})
        assert response.status_code == 200  

    def test_get_response_missing_prompt(self, test_client, mock_db, mock_openai):
        response = test_client.post('/get_response', json={"user_id": "123", "personality": "Helpful Mom"})
        assert response.status_code == 400
        assert "No input provided" in response.data.decode()

    def test_get_response_missing_user_id(self, test_client, mock_db, mock_openai):
        response = test_client.post('/get_response', json={"prompt": "Hello", "personality": "Helpful Mom"})
        assert response.status_code == 400
        assert "No input provided" in response.data.decode()

    def test_reset_conversation_missing_user_id(self, test_client):
        response = test_client.post('/reset_conversation', json={})
        assert response.status_code == 400
        assert "User ID is required" in response.data.decode()
