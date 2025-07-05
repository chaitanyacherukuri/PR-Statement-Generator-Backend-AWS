"""
Pytest configuration and fixtures for the PR Statement Generator Backend tests.
"""

import os
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Set test environment variables before importing the app
os.environ["GROQ_API_KEY"] = "test-api-key"
os.environ["LOG_LEVEL"] = "ERROR"  # Reduce logging noise during tests

# Import the app - we'll mock initialization in individual tests
from main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    # Mock the initialization to prevent real API calls during testing
    with patch("services.pr_generator.initialize_pr_generator"):
        with patch("main._pr_generator_initialized", True):
            with TestClient(app) as test_client:
                yield test_client


@pytest.fixture
async def async_client():
    """Create an async test client for the FastAPI application."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_pr_generator():
    """Mock the PR generator service to avoid external dependencies."""
    with patch("main._pr_generator_initialized", True):
        with patch("services.pr_generator.generate_pr_statement", new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = "This is a test PR statement for testing purposes."
            yield mock_generate


@pytest.fixture
def mock_pr_generator_not_initialized():
    """Mock the PR generator service as not initialized."""
    with patch("main._pr_generator_initialized", False):
        yield


@pytest.fixture
def mock_pr_generator_error():
    """Mock the PR generator service to raise an error."""
    with patch("main._pr_generator_initialized", True):
        with patch("services.pr_generator.generate_pr_statement", new_callable=AsyncMock) as mock_generate:
            mock_generate.side_effect = Exception("Test error")
            yield mock_generate


@pytest.fixture
def mock_initialization_error():
    """Mock initialization to fail during startup."""
    with patch("services.pr_generator.initialize_pr_generator") as mock_init:
        mock_init.side_effect = Exception("Initialization failed")
        yield mock_init
