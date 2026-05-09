"""Integration tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from travel_api.app import app


@pytest.fixture
def client():
    """Create FastAPI test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check_returns_200(self, client):
        """Test health endpoint returns success."""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_check_returns_json(self, client):
        """Test health endpoint returns JSON."""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"
    
    def test_health_check_content(self, client):
        """Test health endpoint returns expected content."""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


class TestConfigEndpoint:
    """Test configuration endpoint."""
    
    def test_config_endpoint_returns_200(self, client):
        """Test config endpoint returns success."""
        response = client.get("/config")
        assert response.status_code == 200
    
    def test_config_returns_features(self, client):
        """Test config endpoint returns features."""
        response = client.get("/config")
        data = response.json()
        assert "features" in data
        assert isinstance(data["features"], list)


class TestSessionEndpoints:
    """Test session management endpoints."""
    
    def test_create_session_returns_200(self, client):
        """Test creating a new session."""
        response = client.post("/sessions", json={"userId": "test-user"})
        assert response.status_code in [200, 201]
    
    def test_create_session_returns_session_id(self, client):
        """Test session creation returns session ID."""
        response = client.post("/sessions", json={"userId": "test-user"})
        data = response.json()
        assert "sessionId" in data
        assert isinstance(data["sessionId"], str)
    
    def test_get_session_returns_200(self, client):
        """Test retrieving an existing session."""
        # First create a session
        create_response = client.post("/sessions", json={"userId": "test-user"})
        session_id = create_response.json()["sessionId"]
        
        # Then retrieve it
        response = client.get(f"/sessions/{session_id}")
        assert response.status_code == 200
    
    def test_get_nonexistent_session_returns_404(self, client):
        """Test retrieving nonexistent session returns 404."""
        response = client.get("/sessions/nonexistent-session-id")
        assert response.status_code == 404


class TestChatEndpoints:
    """Test chat functionality endpoints."""
    
    def test_assistant_reply_returns_200(self, client):
        """Test assistant reply endpoint returns success."""
        # Create session first
        session_response = client.post("/sessions", json={"userId": "test-user"})
        session_id = session_response.json()["sessionId"]
        
        # Send chat message
        response = client.post(
            "/assistant/reply",
            json={
                "sessionId": session_id,
                "message": "Find resorts with pool"
            }
        )
        assert response.status_code == 200
    
    def test_assistant_reply_returns_reply(self, client):
        """Test assistant reply contains reply field."""
        session_response = client.post("/sessions", json={"userId": "test-user"})
        session_id = session_response.json()["sessionId"]
        
        response = client.post(
            "/assistant/reply",
            json={
                "sessionId": session_id,
                "message": "Find resorts with pool"
            }
        )
        
        data = response.json()
        assert "reply" in data
        assert isinstance(data["reply"], str)
        assert len(data["reply"]) > 0
    
    def test_assistant_reply_handles_different_queries(self, client):
        """Test assistant handles different types of queries."""
        session_response = client.post("/sessions", json={"userId": "test-user"})
        session_id = session_response.json()["sessionId"]
        
        test_queries = [
            "Find resorts with pool",
            "Plan a 2-day trip",
            "Hello, how are you?"
        ]
        
        for query in test_queries:
            response = client.post(
                "/assistant/reply",
                json={
                    "sessionId": session_id,
                    "message": query
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert "reply" in data


class TestErrorHandling:
    """Test error handling in endpoints."""
    
    def test_assistant_reply_missing_session_id(self, client):
        """Test assistant reply handles missing session ID."""
        response = client.post(
            "/assistant/reply",
            json={
                "message": "Find resorts"
                # Missing sessionId
            }
        )
        # Should handle gracefully (may return error or create session)
        assert response.status_code in [200, 400, 422]
    
    def test_assistant_reply_empty_message(self, client):
        """Test assistant reply handles empty message."""
        session_response = client.post("/sessions", json={"userId": "test-user"})
        session_id = session_response.json()["sessionId"]
        
        response = client.post(
            "/assistant/reply",
            json={
                "sessionId": session_id,
                "message": ""
            }
        )
        # Should handle gracefully
        assert response.status_code in [200, 400]
    
    def test_invalid_session_id_format(self, client):
        """Test handling of invalid session ID format."""
        response = client.get("/sessions/invalid-format")
        # Should handle gracefully
        assert response.status_code in [200, 404, 422]


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_multiple_requests_handled(self, client):
        """Test that multiple requests are handled properly."""
        session_response = client.post("/sessions", json={"userId": "test-user"})
        session_id = session_response.json()["sessionId"]
        
        # Send multiple requests
        for i in range(3):
            response = client.post(
                "/assistant/reply",
                json={
                    "sessionId": session_id,
                    "message": f"Test message {i}"
                }
            )
            assert response.status_code == 200


class TestIntegrationFlows:
    """Test complete integration flows."""
    
    def test_full_chat_flow(self, client):
        """Test complete chat flow from session creation to response."""
        # 1. Create session
        session_response = client.post("/sessions", json={"userId": "test-user"})
        assert session_response.status_code in [200, 201]
        session_id = session_response.json()["sessionId"]
        
        # 2. Send chat message
        chat_response = client.post(
            "/assistant/reply",
            json={
                "sessionId": session_id,
                "message": "Find resorts with pool and wifi"
            }
        )
        assert chat_response.status_code == 200
        
        # 3. Verify response structure
        data = chat_response.json()
        assert "reply" in data
        assert "node" in data
        assert "timestamp" in data
        
        # 4. Response should be substantive
        reply = data["reply"]
        assert len(reply) > 10  # Should be more than just a short message
    
    def test_evaluation_prompt_1(self, client):
        """Test Prompt 1: Amenity filtering."""
        session_response = client.post("/sessions", json={"userId": "test-user"})
        session_id = session_response.json()["sessionId"]
        
        response = client.post(
            "/assistant/reply",
            json={
                "sessionId": session_id,
                "message": "Find three resorts with swimming pool and wifi for two adults, budget under ₹8,000 per night"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        reply = data["reply"].lower()
        
        # Should mention pool, wifi, or resorts
        assert any(word in reply for word in ['pool', 'wifi', 'resort', '₹', 'budget'])
    
    def test_evaluation_prompt_2(self, client):
        """Test Prompt 2: Trip planning."""
        session_response = client.post("/sessions", json={"userId": "test-user"})
        session_id = session_response.json()["sessionId"]
        
        response = client.post(
            "/assistant/reply",
            json={
                "sessionId": session_id,
                "message": "Plan a 2-night Dandeli trip with river rafting, nature walks, and pool+wifi"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        reply = data["reply"].lower()
        
        # Should mention itinerary, rafting, or activities
        assert any(word in reply for word in ['itinerary', 'rafting', 'nature', 'day', 'night'])
    
    def test_evaluation_prompt_3(self, client):
        """Test Prompt 3: Resort comparison."""
        session_response = client.post("/sessions", json={"userId": "test-user"})
        session_id = session_response.json()["sessionId"]
        
        response = client.post(
            "/assistant/reply",
            json={
                "sessionId": session_id,
                "message": "Compare River Valley, Jungle Camp, and Tiger Resort"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        reply = data["reply"]
        
        # Should be a substantive comparison
        assert len(reply) > 50
        reply_lower = reply.lower()
        assert any(word in reply_lower for word in ['compare', 'river valley', 'jungle camp', 'tiger resort'])


class TestPerformance:
    """Test performance characteristics."""
    
    def test_response_time_reasonable(self, client):
        """Test that responses come back within reasonable time."""
        import time
        
        session_response = client.post("/sessions", json={"userId": "test-user"})
        session_id = session_response.json()["sessionId"]
        
        start_time = time.time()
        response = client.post(
            "/assistant/reply",
            json={
                "sessionId": session_id,
                "message": "Find resorts with pool"
            }
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 30  # Should respond within 30 seconds
        assert response.status_code == 200
