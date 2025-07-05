"""
Unit tests for Pydantic models.

Tests validate model behavior, field validation, and serialization/deserialization.
"""

import pytest
from pydantic import ValidationError

from models import PRStatementRequest, PRStatementResponse, HealthResponse, Feedback


class TestPRStatementRequest:
    """Test cases for PRStatementRequest model."""

    def test_valid_request_creation(self):
        """Test creating a valid PR statement request."""
        request = PRStatementRequest(topic="AI chatbot launch")
        assert request.topic == "AI chatbot launch"

    def test_topic_minimum_length_validation(self):
        """Test topic minimum length validation."""
        with pytest.raises(ValidationError) as exc_info:
            PRStatementRequest(topic="")
        
        errors = exc_info.value.errors()
        assert any("min_length" in str(error) for error in errors)

    def test_topic_maximum_length_validation(self):
        """Test topic maximum length validation."""
        long_topic = "x" * 501  # Exceeds max_length=500
        
        with pytest.raises(ValidationError) as exc_info:
            PRStatementRequest(topic=long_topic)
        
        errors = exc_info.value.errors()
        assert any("max_length" in str(error) for error in errors)

    def test_topic_boundary_lengths(self):
        """Test topic at boundary lengths."""
        # Test minimum valid length
        request = PRStatementRequest(topic="A")
        assert request.topic == "A"
        
        # Test maximum valid length
        max_topic = "x" * 500
        request = PRStatementRequest(topic=max_topic)
        assert request.topic == max_topic
        assert len(request.topic) == 500

    def test_missing_topic_field(self):
        """Test validation when topic field is missing."""
        with pytest.raises(ValidationError) as exc_info:
            PRStatementRequest()
        
        errors = exc_info.value.errors()
        assert any(error["type"] == "missing" for error in errors)

    def test_topic_type_validation(self):
        """Test topic type validation."""
        with pytest.raises(ValidationError):
            PRStatementRequest(topic=123)  # Should be string
        
        with pytest.raises(ValidationError):
            PRStatementRequest(topic=None)

    def test_request_serialization(self):
        """Test request model serialization."""
        request = PRStatementRequest(topic="Test topic")
        data = request.model_dump()
        
        assert data == {"topic": "Test topic"}
        assert isinstance(data["topic"], str)

    def test_request_json_serialization(self):
        """Test request model JSON serialization."""
        request = PRStatementRequest(topic="Test topic")
        json_str = request.model_dump_json()

        assert '"topic":"Test topic"' in json_str or '"topic": "Test topic"' in json_str


class TestPRStatementResponse:
    """Test cases for PRStatementResponse model."""

    def test_valid_response_creation(self):
        """Test creating a valid PR statement response."""
        response = PRStatementResponse(
            pr_statement="Test PR statement",
            status="success",
            message="Generated successfully"
        )
        
        assert response.pr_statement == "Test PR statement"
        assert response.status == "success"
        assert response.message == "Generated successfully"

    def test_response_with_default_message(self):
        """Test response creation with default message."""
        response = PRStatementResponse(
            pr_statement="Test PR statement",
            status="success"
        )
        
        assert response.message == ""  # Default value

    def test_status_literal_validation(self):
        """Test status field literal validation."""
        # Valid statuses
        response = PRStatementResponse(pr_statement="test", status="success")
        assert response.status == "success"
        
        response = PRStatementResponse(pr_statement="test", status="error")
        assert response.status == "error"
        
        # Invalid status
        with pytest.raises(ValidationError) as exc_info:
            PRStatementResponse(pr_statement="test", status="invalid")
        
        errors = exc_info.value.errors()
        assert any("literal_error" in str(error) or "Input should be" in str(error) for error in errors)

    def test_missing_required_fields(self):
        """Test validation when required fields are missing."""
        with pytest.raises(ValidationError):
            PRStatementResponse()
        
        with pytest.raises(ValidationError):
            PRStatementResponse(pr_statement="test")  # Missing status
        
        with pytest.raises(ValidationError):
            PRStatementResponse(status="success")  # Missing pr_statement

    def test_response_serialization(self):
        """Test response model serialization."""
        response = PRStatementResponse(
            pr_statement="Test statement",
            status="success",
            message="Success message"
        )
        
        data = response.model_dump()
        expected = {
            "pr_statement": "Test statement",
            "status": "success",
            "message": "Success message"
        }
        assert data == expected


class TestHealthResponse:
    """Test cases for HealthResponse model."""

    def test_valid_health_response_creation(self):
        """Test creating a valid health response."""
        response = HealthResponse(
            status="healthy",
            message="Service is running"
        )
        
        assert response.status == "healthy"
        assert response.message == "Service is running"

    def test_missing_required_fields(self):
        """Test validation when required fields are missing."""
        with pytest.raises(ValidationError):
            HealthResponse()
        
        with pytest.raises(ValidationError):
            HealthResponse(status="healthy")  # Missing message
        
        with pytest.raises(ValidationError):
            HealthResponse(message="test")  # Missing status

    def test_field_types(self):
        """Test field type validation."""
        with pytest.raises(ValidationError):
            HealthResponse(status=123, message="test")
        
        with pytest.raises(ValidationError):
            HealthResponse(status="healthy", message=456)

    def test_health_response_serialization(self):
        """Test health response serialization."""
        response = HealthResponse(status="healthy", message="All good")
        data = response.model_dump()
        
        expected = {"status": "healthy", "message": "All good"}
        assert data == expected


class TestFeedback:
    """Test cases for Feedback model."""

    def test_valid_feedback_creation(self):
        """Test creating valid feedback."""
        feedback = Feedback(
            grade="good",
            feedback="The statement is well-formed"
        )
        
        assert feedback.grade == "good"
        assert feedback.feedback == "The statement is well-formed"

    def test_grade_literal_validation(self):
        """Test grade field literal validation."""
        # Valid grades
        feedback = Feedback(grade="good", feedback="test")
        assert feedback.grade == "good"
        
        feedback = Feedback(grade="needs improvement", feedback="test")
        assert feedback.grade == "needs improvement"
        
        # Invalid grade
        with pytest.raises(ValidationError) as exc_info:
            Feedback(grade="invalid", feedback="test")
        
        errors = exc_info.value.errors()
        assert any("literal_error" in str(error) or "Input should be" in str(error) for error in errors)

    def test_missing_required_fields(self):
        """Test validation when required fields are missing."""
        with pytest.raises(ValidationError):
            Feedback()
        
        with pytest.raises(ValidationError):
            Feedback(grade="good")  # Missing feedback
        
        with pytest.raises(ValidationError):
            Feedback(feedback="test")  # Missing grade

    def test_feedback_serialization(self):
        """Test feedback model serialization."""
        feedback = Feedback(grade="needs improvement", feedback="Add more details")
        data = feedback.model_dump()
        
        expected = {"grade": "needs improvement", "feedback": "Add more details"}
        assert data == expected
