# Configures shared pytest fixtures and test setup helpers.
# File: tests/conftest.py


"""Pytest configuration and shared fixtures."""
import sys
import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / '.env')


@pytest.fixture(scope="session")
def test_data_dir():
    """Return path to test data directory."""
    return PROJECT_ROOT / "data" / "json_files"


@pytest.fixture
def mock_request():
    """Create mock FastAPI request object."""
    mock = MagicMock()
    mock.client.host = "127.0.0.1"
    mock.headers.get.return_value = "test-agent"
    return mock


@pytest.fixture
def sample_resort():
    """Return sample resort data for testing."""
    return {
        'id': 'test-resort-1',
        'name': 'Test Resort',
        'location': 'Dandeli',
        'description': 'A beautiful test resort',
        'price': 5000,
        'rating': 4.5,
        'amenities': ['pool', 'wifi', 'restaurant', 'spa'],
        'contact_info': {
            'phone': '9876543210',
            'email': 'test@resort.com'
        },
        'booking_url': 'https://example.com/book'
    }


@pytest.fixture
def sample_resorts_list(sample_resort):
    """Return list of sample resorts."""
    return [
        {
            **sample_resort,
            'id': 'river-valley',
            'name': 'River Valley'
        },
        {
            **sample_resort,
            'id': 'jungle-camp',
            'name': 'Jungle Camp',
            'amenities': ['pool', 'wifi', 'restaurant', 'nature-trails']
        },
        {
            **sample_resort,
            'id': 'tiger-resort',
            'name': 'Tiger Resort',
            'price': 6500,
            'amenities': ['pool', 'wifi', 'restaurant', 'rafting']
        }
    ]


@pytest.fixture
def sample_search_filters():
    """Return sample search filters."""
    from travel_tools.search_engine import SearchFilters
    return SearchFilters(
        min_rating=3.5,
        max_budget=8000,
        guest_count=2,
        family_friendly=True
    )


@pytest.fixture
def sample_session_state():
    """Return sample graph state for testing."""
    return {
        'messages': [('user', 'Find resorts with pool')],
        'session_id': 'test-session-123',
        'user_id': 'test-user-456',
        'history': []
    }


@pytest.fixture
def test_client():
    """Create FastAPI test client."""
    from fastapi.testclient import TestClient
    from travel_api.app import app
    return TestClient(app)


# Markers for test categorization
def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line(
        "markers", "asyncio: marks tests as async"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


@pytest.fixture(autouse=True)
def reset_api_counter():
    """Reset API call counter before each test."""
    from travel_agents import llms
    llms._api_call_counter = 0
    yield
    llms._api_call_counter = 0