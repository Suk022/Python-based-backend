import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.config import settings

# Force SQLite for tests
os.environ["USE_SQLITE"] = "true"

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    # Create tables
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    # Clean up
    Base.metadata.drop_all(bind=engine)

def test_register_and_login(client):
    """Test user registration and login flow"""
    # Register user
    register_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = client.post("/auth/register", json=register_data)
    assert response.status_code == 200
    assert "User registered successfully" in response.json()["message"]
    
    # Login user
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    
    return data["access_token"]

def test_paragraph_submission_and_search(client):
    """Test paragraph submission and word search functionality"""
    # First register and login
    access_token = test_register_and_login(client)
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Submit paragraphs with repeated word "apple"
    paragraphs_data = {
        "paragraphs": [
            "I love eating apple pie. Apple is my favorite fruit. Apple apple apple!",
            "The apple tree in my garden produces sweet apples every year.",
            "Apple juice is refreshing. I drink apple juice daily with my apple."
        ]
    }
    
    response = client.post("/paragraphs/", json=paragraphs_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Created 3 paragraphs"
    assert len(data["paragraph_ids"]) == 3
    
    # Wait a moment for indexing (in SQLite mode it should be synchronous via BackgroundTasks)
    import time
    time.sleep(1)
    
    # Search for "apple"
    response = client.get("/paragraphs/search?word=apple", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["word"] == "apple"
    assert len(data["results"]) > 0
    
    # Check that results are ordered by word count (descending)
    word_counts = [result["word_count"] for result in data["results"]]
    assert word_counts == sorted(word_counts, reverse=True)
    
    # The first paragraph should have the highest count (5 occurrences of "apple")
    assert data["results"][0]["word_count"] >= 4

def test_word_count_accumulation(client):
    """Test that word counts accumulate across multiple submissions"""
    # Register a new user for this test
    register_data = {
        "email": "test2@example.com", 
        "password": "testpassword123"
    }
    client.post("/auth/register", json=register_data)
    
    # Login
    login_data = {
        "email": "test2@example.com",
        "password": "testpassword123"
    }
    response = client.post("/auth/login", json=login_data)
    access_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # First submission
    paragraphs_data1 = {
        "paragraphs": ["The cat sat on the mat. The cat was happy."]
    }
    client.post("/paragraphs/", json=paragraphs_data1, headers=headers)
    
    # Second submission
    paragraphs_data2 = {
        "paragraphs": ["The dog and the cat played together. The cat loves the dog."]
    }
    client.post("/paragraphs/", json=paragraphs_data2, headers=headers)
    
    # Wait for indexing
    import time
    time.sleep(1)
    
    # Search for "the" - should appear in both submissions
    response = client.get("/paragraphs/search?word=the", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["word"] == "the"
    assert len(data["results"]) == 2  # Should find both paragraphs
    
    # Total occurrences should be accumulated
    total_the_count = sum(result["word_count"] for result in data["results"])
    assert total_the_count >= 6  # "the" appears multiple times across both paragraphs
