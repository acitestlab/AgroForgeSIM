"""
🧩 AgroForgeSIM Test Configuration
---------------------------------
Provides shared pytest fixtures for API and engine tests.

This module sets up a reusable FastAPI `TestClient` fixture
for use across all backend test files. It ensures:
- Consistent app context
- Improved performance via session-scoped fixture
- Simplified API endpoint testing in CI/CD
"""

import pytest
from fastapi.testclient import TestClient
from backend.app import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    """
    Pytest fixture that provides a reusable FastAPI test client.

    Usage:
        def test_health_endpoint(client):
            response = client.get("/api/health")
            assert response.status_code == 200
            assert response.json()["status"] == "ok"
    """
    return TestClient(app)
