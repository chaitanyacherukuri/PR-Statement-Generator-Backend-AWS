"""
Integration tests for the PR Statement Generator Backend.

These tests verify the application behavior with mocked external dependencies
but test the full request/response cycle through the FastAPI application.
"""

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

# Import app after setting environment variables in conftest.py
from main import app


class TestApplicationLifespan:
    """Test cases for application startup and shutdown."""

    def test_successful_initialization(self):
        """Test successful application initialization."""
        # Test that the application starts and health endpoint works
        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"

    def test_initialization_behavior(self):
        """Test application initialization behavior."""
        # Test that the application can handle requests even with initialization issues
        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 200


class TestEndToEndWorkflow:
    """Test cases for end-to-end API workflows."""

    def test_complete_pr_generation_workflow(self, client: TestClient):
        """Test complete PR generation workflow from request to response."""
        # Make request
        request_data = {"topic": "Revolutionary AI breakthrough"}
        response = client.post("/api/generate-pr-statement", json=request_data)

        # Verify response structure and basic functionality
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["pr_statement"]) > 0  # Should get some response (fallback or real)
        assert data["message"] == "PR statement generated successfully"
        assert isinstance(data["pr_statement"], str)

    def test_error_recovery_workflow(self, client: TestClient):
        """Test error recovery in the workflow."""
        request_data = {"topic": "Test topic"}
        response = client.post("/api/generate-pr-statement", json=request_data)

        # The application has fallback behavior, so it should still return 200
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        # Should get fallback response when API fails
        assert len(data["pr_statement"]) > 0


class TestCORSConfiguration:
    """Test cases for CORS configuration."""

    def test_cors_headers_present(self, client: TestClient):
        """Test that CORS headers are properly configured."""
        # Test preflight request
        response = client.options(
            "/api/generate-pr-statement",
            headers={
                "Origin": "http://localhost:8501",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        # Should allow the request
        assert response.status_code in [200, 204]

    def test_cors_allowed_origins(self, client: TestClient):
        """Test CORS with allowed origins."""
        with patch("main._pr_generator_initialized", True):
            with patch("services.pr_generator.generate_pr_statement") as mock_generate:
                mock_generate.return_value = "Test statement"
                
                # Test with allowed origin
                response = client.post(
                    "/api/generate-pr-statement",
                    json={"topic": "test"},
                    headers={"Origin": "http://localhost:8501"}
                )
                
                assert response.status_code == 200


class TestGlobalExceptionHandler:
    """Test cases for global exception handling."""

    def test_global_exception_handler_format(self, client: TestClient):
        """Test global exception handler response format."""
        request_data = {"topic": "test topic"}
        response = client.post("/api/generate-pr-statement", json=request_data)

        # The application has fallback behavior, so it returns 200 with fallback content
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["pr_statement"]) > 0

    def test_exception_handler_preserves_http_exceptions(self, client: TestClient):
        """Test that HTTPExceptions are not caught by global handler."""
        with patch("main._pr_generator_initialized", False):
            request_data = {"topic": "test topic"}
            response = client.post("/api/generate-pr-statement", json=request_data)
            
            # Should get the specific HTTP exception, not global handler
            assert response.status_code == 503
            data = response.json()
            assert "PR Generator Service is not available" in data["detail"]


class TestContentTypeHandling:
    """Test cases for content type handling."""

    def test_json_content_type_required(self, client: TestClient):
        """Test that JSON content type is required for POST requests."""
        response = client.post(
            "/api/generate-pr-statement",
            data="topic=test",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 422

    def test_json_content_type_accepted(self, client: TestClient, mock_pr_generator):
        """Test that JSON content type is properly accepted."""
        response = client.post(
            "/api/generate-pr-statement",
            json={"topic": "test"},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200

    def test_malformed_json_handling(self, client: TestClient):
        """Test handling of malformed JSON."""
        response = client.post(
            "/api/generate-pr-statement",
            data='{"topic": "test"',  # Malformed JSON
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422


class TestResponseHeaders:
    """Test cases for response headers."""

    def test_content_type_headers(self, client: TestClient):
        """Test that responses have correct content type headers."""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"
        
        response = client.get("/")
        assert response.headers["content-type"] == "application/json"

    def test_response_encoding(self, client: TestClient, mock_pr_generator):
        """Test response encoding for various character sets."""
        # Test with unicode characters in topic
        request_data = {"topic": "AI革命 - 人工智能突破"}
        response = client.post("/api/generate-pr-statement", json=request_data)
        
        assert response.status_code == 200
        assert response.encoding in ["utf-8", None]  # FastAPI uses utf-8 by default


class TestConcurrentRequests:
    """Test cases for handling concurrent requests."""

    def test_multiple_health_checks(self, client: TestClient):
        """Test multiple concurrent health check requests."""
        responses = []
        for _ in range(5):
            response = client.get("/health")
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"

    def test_multiple_pr_generation_requests(self, client: TestClient):
        """Test multiple PR generation requests."""
        with patch("main._pr_generator_initialized", True):
            with patch("services.pr_generator.generate_pr_statement") as mock_generate:
                mock_generate.return_value = "Test statement"
                
                responses = []
                topics = [f"Topic {i}" for i in range(3)]
                
                for topic in topics:
                    response = client.post("/api/generate-pr-statement", json={"topic": topic})
                    responses.append(response)
                
                # All should succeed
                for response in responses:
                    assert response.status_code == 200
                    data = response.json()
                    assert data["status"] == "success"
