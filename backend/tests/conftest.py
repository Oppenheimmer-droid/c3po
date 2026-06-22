"""
Pytest configuration and fixtures for backend tests.
"""

import pytest
import asyncio
from typing import AsyncGenerator


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    from app.core.settings import Settings
    return Settings(
        ENVIRONMENT="test",
        DEBUG=True,
        DATABASE_URL="postgresql+asyncpg://test:test@localhost:5432/test",
        SECRET_KEY="test-secret-key-for-testing-only",
        GROQ_API_KEY="test-groq-key",
        OPENAI_API_KEY="test-openai-key",
    )
