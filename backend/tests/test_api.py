"""
API endpoint tests
"""
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app


class TestAPI:
    """Test API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "LLM Analysis Quiz Bot"
        assert data["status"] == "running"
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_history_endpoint(self):
        """Test history endpoint"""
        client = TestClient(app)
        response = client.get("/history")
        
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert isinstance(data["history"], list)
    
    def test_quiz_invalid_json(self):
        """Test quiz endpoint with invalid JSON"""
        client = TestClient(app)
        response = client.post(
            "/quiz",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400
    
    def test_quiz_invalid_secret(self):
        """Test quiz endpoint with invalid secret"""
        client = TestClient(app)
        response = client.post(
            "/quiz",
            json={
                "email": "test@example.com",
                "secret": "wrong-secret",
                "url": "https://example.com/quiz"
            }
        )
        
        assert response.status_code == 403
    
    def test_quiz_valid_request_structure(self):
        """Test quiz endpoint with valid structure"""
        client = TestClient(app)
        
        # This will fail on actual processing but should validate structure
        response = client.post(
            "/quiz",
            json={
                "email": "test@example.com",
                "secret": "default-secret-change-me",
                "url": "https://httpbin.org/html"
            }
        )
        
        # Should return 200 even if processing fails (error in response body)
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "steps" in data
        assert "time_taken" in data
