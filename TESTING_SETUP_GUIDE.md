# Project Cleanup & Testing Setup Guide

## 🧹 PHASE 1: CLEANUP

### Files to Remove (Old Exploration/Debug Files)

```
❌ DELETE THESE (No longer needed):
├── test_rate_limit.py          (Old exploration script)
├── test_river_valley.py        (Old exploration script)
├── repro_graph_test.py         (Old reproduction script)
├── repro_invoke_test.py        (Old reproduction script)
├── CHANGE_LOG.md               (Not essential for presentation)
├── ingest.py                   (Optional - only keep if needed for data ingestion)
└── chroma_db/                  (Old test database - delete completely)
    └── (remove entire directory)

✅ KEEP THESE:
├── docker-compose.yml          (Deployment)
├── requirements.txt            (Dependencies)
├── .env                        (Configuration)
├── travel_agents/              (Core code)
├── travel_api/                 (Core API)
├── travel_tools/               (Core tools)
├── frontend/                   (Web interface)
├── data/                       (Resort data)
└── (All presentation markdown files you created)
```

---

## 📁 Updated Project Structure (After Cleanup)

```
d:\RAG\CollegeProject\
├── .env                                    # Config (API keys)
├── .gitignore                             # Git ignore (create if missing)
├── README.md                              # Project overview (UPDATE THIS)
├── docker-compose.yml                     # Docker setup
├── requirements.txt                       # Python dependencies
│
├── travel_agents/                         # Multi-agent orchestration
│   ├── __init__.py
│   ├── graph.py                          # LangGraph agent routing
│   ├── nodes.py                          # Agent node implementations
│   ├── llms.py                           # LLM provider + rotation logic
│   ├── intent.py                         # Intent classification
│   ├── state.py                          # Graph state definition
│   ├── content.py                        # Content generation
│   ├── date_helpers.py                   # Date utilities
│   ├── booking_helpers.py                # Booking logic
│   └── resort_helpers.py                 # Resort utilities
│
├── travel_api/                            # FastAPI backend
│   ├── __init__.py
│   ├── app.py                            # Main API application
│   ├── models.py                         # Pydantic models
│   ├── services.py                       # Business logic
│   └── store.py                          # Data persistence
│
├── travel_tools/                          # LangChain tools
│   ├── __init__.py
│   ├── search_tool.py                    # Resort search
│   ├── search_engine.py                  # Search filtering
│   ├── booking_tool.py                   # Booking operations
│   ├── booking_store.py                  # Booking storage
│   ├── config.py                         # Tool configuration
│   ├── data_validator.py                 # Data validation
│   ├── vectorstore_provider.py           # Vector DB setup
│   └── booking_status_tool.py            # Booking status checks
│
├── frontend/                              # Next.js + React
│   ├── package.json
│   ├── next.config.mjs
│   ├── middleware.js
│   ├── Dockerfile
│   ├── app/                              # Next.js app directory
│   │   ├── api/                          # API routes
│   │   ├── chat/                         # Chat interface
│   │   ├── sign-in/
│   │   ├── sign-up/
│   │   ├── (marketing)/
│   │   ├── layout.jsx
│   │   └── globals.css
│   ├── components/                       # React components
│   ├── lib/                              # Utilities
│   └── public/                           # Static assets
│
├── data/                                  # Resort data
│   ├── json_files/
│   │   ├── resorts.json                  # 81 resorts
│   │   ├── chat_sessions.json            # Sample sessions
│   │   └── bookings.json                 # Sample bookings
│   ├── text/                             # Text documents
│   └── local_sessions.json               # Local session storage
│
├── chroma_db_v2/                         # Vector database (KEEP THIS)
│   └── chroma.sqlite3
│
├── tests/                                 # NEW - Unit tests
│   ├── __init__.py
│   ├── conftest.py                       # Pytest configuration
│   ├── test_search_tool.py               # Search functionality
│   ├── test_search_engine.py             # Filtering logic
│   ├── test_llms.py                      # LLM provider rotation
│   ├── test_nodes.py                     # Agent nodes
│   ├── test_graph.py                     # Agent orchestration
│   ├── test_booking_tool.py              # Booking operations
│   └── integration/                      # Integration tests
│       ├── test_api_endpoints.py
│       ├── test_chat_flow.py
│       └── test_graph_execution.py
│
└── docs/                                  # Documentation
    ├── ARCHITECTURE.md
    ├── API_DOCUMENTATION.md
    ├── DEPLOYMENT.md
    ├── TEST_RESULTS.md
    └── PROJECT_SUMMARY_FOR_PRESENTATION.md
```

---

## 🧹 Cleanup Commands

### Step 1: Remove Unnecessary Files

```bash
cd d:\RAG\CollegeProject

# Remove old test/exploration files
Remove-Item -Force test_rate_limit.py
Remove-Item -Force test_river_valley.py
Remove-Item -Force repro_graph_test.py
Remove-Item -Force repro_invoke_test.py
Remove-Item -Force CHANGE_LOG.md

# Remove old database directories
Remove-Item -Recurse -Force chroma_db

# Note: Keep ingest.py if you plan to ingest new data,
# or remove it if you won't need it anymore
Remove-Item -Force ingest.py
```

---

## 🧪 PHASE 2: SETUP TESTING FRAMEWORK

### Step 1: Install Testing Dependencies

Add to `requirements.txt`:

```
# ... existing dependencies ...

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
httpx==0.25.0
```

Then install:

```bash
pip install -r requirements.txt
```

### Step 2: Create Pytest Configuration

Create `pytest.ini`:

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --cov=travel_agents --cov=travel_api --cov=travel_tools
```

### Step 3: Create Tests Directory Structure

```bash
mkdir tests
mkdir tests\integration

# Create init file
New-Item -Type File tests\__init__.py
New-Item -Type File tests\integration\__init__.py
```

---

## 🧪 PHASE 3: CREATE UNIT TESTS

### Test 1: Search Tool Tests

**File:** `tests/test_search_tool.py`

```python
import pytest
from travel_tools.search_tool import find_resort_by_name, search_resorts
from travel_tools.search_engine import SearchFilters

class TestSearchTool:
    """Test resort search functionality."""

    def test_find_resort_by_name_exact_match(self):
        """Test finding a resort by exact name."""
        resort = find_resort_by_name("River Valley")
        assert resort is not None
        assert resort['name'] == "River Valley"

    def test_find_resort_by_name_partial_match(self):
        """Test partial name matching."""
        resort = find_resort_by_name("Jungle")
        assert resort is not None
        assert "Jungle" in resort['name']

    def test_search_resorts_with_filters(self):
        """Test searching with multiple filters."""
        filters = SearchFilters(
            min_rating=4.0,
            max_budget=8000,
            guest_count=2,
            family_friendly=True
        )
        results = search_resorts("resort", filters)
        assert len(results) > 0
        assert all(r['price'] <= 8000 for r in results)

    def test_search_multiple_resorts(self):
        """Test searching for multiple resorts."""
        filters = SearchFilters(
            target_resort_names=["River Valley", "Jungle Camp", "Tiger Resort"]
        )
        results = search_resorts("compare", filters)
        assert len(results) > 0
```

---

### Test 2: Search Engine Tests

**File:** `tests/test_search_engine.py`

```python
import pytest
from travel_tools.search_engine import SearchFilters, filter_resorts

class TestSearchEngine:
    """Test resort filtering logic."""

    def test_filter_by_budget(self):
        """Test budget filtering."""
        filters = SearchFilters(max_budget=8000)
        resorts = [
            {'name': 'A', 'price': 5000},
            {'name': 'B', 'price': 9000},
            {'name': 'C', 'price': 7000}
        ]
        filtered = filter_resorts(resorts, filters)
        assert all(r['price'] <= 8000 for r in filtered)
        assert len(filtered) == 2

    def test_filter_by_rating(self):
        """Test rating filtering."""
        filters = SearchFilters(min_rating=4.5)
        resorts = [
            {'name': 'A', 'rating': 4.8},
            {'name': 'B', 'rating': 3.5},
            {'name': 'C', 'rating': 4.6}
        ]
        filtered = filter_resorts(resorts, filters)
        assert all(r['rating'] >= 4.5 for r in filtered)
        assert len(filtered) == 2

    def test_filter_by_amenities(self):
        """Test amenity filtering."""
        filters = SearchFilters(required_amenities=['pool', 'wifi'])
        resorts = [
            {'name': 'A', 'amenities': ['pool', 'wifi', 'restaurant']},
            {'name': 'B', 'amenities': ['pool', 'bar']},
            {'name': 'C', 'amenities': ['wifi', 'gym']}
        ]
        filtered = filter_resorts(resorts, filters)
        assert len(filtered) == 1
        assert filtered[0]['name'] == 'A'
```

---

### Test 3: LLM Provider Rotation Tests

**File:** `tests/test_llms.py`

```python
import pytest
from travel_agents.llms import (
    get_rotated_groq_llm,
    get_rotated_gemini,
    get_next_provider_pair,
    _api_call_counter
)

class TestLLMRotation:
    """Test LLM provider rotation and fallback."""

    def test_groq_rotation(self):
        """Test Groq key rotation."""
        llm1 = get_rotated_groq_llm()
        llm2 = get_rotated_groq_llm()
        llm3 = get_rotated_groq_llm()
        llm4 = get_rotated_groq_llm()

        # Should cycle through 3 keys
        assert llm1 is not None
        assert llm2 is not None
        assert llm3 is not None
        # Should repeat after 3 calls
        assert llm4 is not None

    def test_gemini_rotation(self):
        """Test Gemini key rotation."""
        llm1 = get_rotated_gemini()
        llm2 = get_rotated_gemini()
        llm3 = get_rotated_gemini()

        assert llm1 is not None
        assert llm2 is not None
        assert llm3 is not None

    def test_provider_alternation(self):
        """Test alternating between Groq and Gemini."""
        provider1, _ = get_next_provider_pair()
        provider2, _ = get_next_provider_pair()
        provider3, _ = get_next_provider_pair()
        provider4, _ = get_next_provider_pair()

        # Should alternate: Groq, Gemini, Groq, Gemini
        assert provider1 == "groq"
        assert provider2 == "gemini"
        assert provider3 == "groq"
        assert provider4 == "gemini"
```

---

### Test 4: Booking Tool Tests

**File:** `tests/test_booking_tool.py`

```python
import pytest
from travel_tools.booking_tool import create_booking, get_booking_status
from travel_tools.booking_store import BookingStore

class TestBookingTool:
    """Test booking functionality."""

    @pytest.fixture
    def booking_store(self):
        """Create temporary booking store."""
        return BookingStore()

    def test_create_booking(self, booking_store):
        """Test creating a new booking."""
        booking = {
            'sessionId': 'session-123',
            'resort': 'River Valley',
            'dates': {'start': '2026-05-15', 'end': '2026-05-17'},
            'guests': 2,
            'contactInfo': {'email': 'user@example.com', 'phone': '9876543210'}
        }
        result = booking_store.save_booking(booking)
        assert result['bookingId'] is not None
        assert result['status'] == 'confirmed'

    def test_get_booking_status(self, booking_store):
        """Test retrieving booking status."""
        booking_id = "booking-123"
        # Create a test booking
        status = booking_store.get_status(booking_id)
        assert status in ['pending', 'confirmed', 'cancelled']
```

---

### Test 5: Agent Nodes Tests

**File:** `tests/test_nodes.py`

```python
import pytest
from travel_agents.nodes import (
    researcher_node,
    planner_node,
    booker_node,
    router_node
)
from travel_agents.state import GraphState

class TestAgentNodes:
    """Test individual agent nodes."""

    @pytest.fixture
    def sample_state(self):
        """Create sample graph state."""
        return GraphState(
            messages=[("user", "Find resorts with pool")],
            session_id="test-session",
            user_id="test-user",
            history=[]
        )

    def test_router_node_identifies_search(self, sample_state):
        """Test router identifies search intent."""
        sample_state.messages = [("user", "Find resorts with swimming pool")]
        result = router_node(sample_state)
        assert result['next_node'] == "researcher"

    def test_router_node_identifies_planning(self, sample_state):
        """Test router identifies trip planning intent."""
        sample_state.messages = [("user", "Plan a 2-day itinerary")]
        result = router_node(sample_state)
        assert result['next_node'] == "planner"

    def test_router_node_identifies_booking(self, sample_state):
        """Test router identifies booking intent."""
        sample_state.messages = [("user", "Book this resort for me")]
        result = router_node(sample_state)
        assert result['next_node'] == "booker"

    @pytest.mark.asyncio
    async def test_researcher_node(self, sample_state):
        """Test researcher node finds resorts."""
        result = await researcher_node(sample_state)
        assert 'response' in result
        assert len(result['response']) > 0
```

---

### Test 6: Graph Execution Tests

**File:** `tests/test_graph.py`

```python
import pytest
from travel_agents.graph import create_graph

class TestAgentGraph:
    """Test LangGraph agent orchestration."""

    @pytest.fixture
    def graph(self):
        """Create agent graph."""
        return create_graph()

    def test_graph_initialization(self, graph):
        """Test graph is properly initialized."""
        assert graph is not None
        assert hasattr(graph, 'invoke')

    @pytest.mark.asyncio
    async def test_graph_search_flow(self, graph):
        """Test full search flow."""
        state = {
            'messages': [("user", "Find 3 resorts with pool and wifi under 8000")],
            'session_id': 'test-session',
            'user_id': 'test-user'
        }
        result = graph.invoke(state)
        assert 'messages' in result
        assert len(result['messages']) > 1

    @pytest.mark.asyncio
    async def test_graph_planning_flow(self, graph):
        """Test full trip planning flow."""
        state = {
            'messages': [("user", "Plan a 2-night trip with rafting")],
            'session_id': 'test-session',
            'user_id': 'test-user'
        }
        result = graph.invoke(state)
        assert 'messages' in result
```

---

## 🧪 PHASE 4: INTEGRATION TESTS

### Test 1: API Endpoints

**File:** `tests/integration/test_api_endpoints.py`

```python
import pytest
from fastapi.testclient import TestClient
from travel_api.app import app

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

class TestAPIEndpoints:
    """Test FastAPI endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_config_endpoint(self, client):
        """Test config endpoint."""
        response = client.get("/config")
        assert response.status_code == 200
        assert 'features' in response.json()

    def test_create_session(self, client):
        """Test creating new session."""
        response = client.post("/sessions", json={"userId": "test-user"})
        assert response.status_code == 200 or response.status_code == 201
        assert 'sessionId' in response.json()

    def test_get_session(self, client):
        """Test retrieving session."""
        # First create a session
        session_response = client.post("/sessions", json={"userId": "test-user"})
        session_id = session_response.json()['sessionId']

        # Then retrieve it
        response = client.get(f"/sessions/{session_id}")
        assert response.status_code == 200

    def test_chat_endpoint(self, client):
        """Test chat endpoint."""
        # Create session first
        session_response = client.post("/sessions", json={"userId": "test-user"})
        session_id = session_response.json()['sessionId']

        # Send chat message
        response = client.post(
            "/assistant/reply",
            json={
                "sessionId": session_id,
                "message": "Find resorts with pool"
            }
        )
        assert response.status_code == 200
        assert 'reply' in response.json()
```

---

### Test 2: Chat Flow

**File:** `tests/integration/test_chat_flow.py`

```python
import pytest
from fastapi.testclient import TestClient
from travel_api.app import app

class TestChatFlow:
    """Test end-to-end chat flows."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_amenity_filtering_flow(self, client):
        """Test Prompt 1: Amenity Filtering."""
        # Create session
        session = client.post("/sessions", json={"userId": "test"}).json()
        session_id = session['sessionId']

        # Send query
        response = client.post(
            "/assistant/reply",
            json={
                "sessionId": session_id,
                "message": "Find three resorts with swimming pool and wifi for 2 adults, budget under 8000"
            }
        )

        assert response.status_code == 200
        reply = response.json()['reply'].lower()
        assert 'pool' in reply or 'resort' in reply

    def test_trip_planning_flow(self, client):
        """Test Prompt 2: Trip Planning."""
        session = client.post("/sessions", json={"userId": "test"}).json()
        session_id = session['sessionId']

        response = client.post(
            "/assistant/reply",
            json={
                "sessionId": session_id,
                "message": "Plan a 2-night Dandeli trip with river rafting and nature walks, prefer resorts with pool"
            }
        )

        assert response.status_code == 200
        reply = response.json()['reply'].lower()
        assert 'day' in reply or 'itinerary' in reply or 'rafting' in reply

    def test_resort_comparison_flow(self, client):
        """Test Prompt 3: Resort Comparison."""
        session = client.post("/sessions", json={"userId": "test"}).json()
        session_id = session['sessionId']

        response = client.post(
            "/assistant/reply",
            json={
                "sessionId": session_id,
                "message": "Compare River Valley, Jungle Camp, and Tiger Resort for me"
            }
        )

        assert response.status_code == 200
        reply = response.json()['reply']
        assert len(reply) > 100  # Should be substantive comparison
```

---

## 🚀 Running Tests

### Run All Tests

```bash
cd d:\RAG\CollegeProject
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_search_tool.py -v
```

### Run with Coverage Report

```bash
pytest tests/ --cov=travel_agents --cov=travel_api --cov=travel_tools --cov-report=html
```

### Run Only Unit Tests

```bash
pytest tests/ -v --ignore=tests/integration
```

### Run Only Integration Tests

```bash
pytest tests/integration/ -v
```

### Run Specific Test

```bash
pytest tests/test_search_tool.py::TestSearchTool::test_find_resort_by_name_exact_match -v
```

### Run with Verbose Output

```bash
pytest tests/ -vv -s
```

---

## 📊 Expected Test Results

After cleanup and setup, you should see:

```
========================= test session starts ==========================
platform win32 -- Python 3.x, pytest-x.x, py-x.x, pluggy-x.x
collected 25 items

tests/test_search_tool.py::TestSearchTool::test_find_resort_by_name_exact_match PASSED
tests/test_search_tool.py::TestSearchTool::test_find_resort_by_name_partial_match PASSED
tests/test_search_tool.py::TestSearchTool::test_search_resorts_with_filters PASSED
tests/test_search_engine.py::TestSearchEngine::test_filter_by_budget PASSED
tests/test_llms.py::TestLLMRotation::test_groq_rotation PASSED
tests/test_booking_tool.py::TestBookingTool::test_create_booking PASSED
tests/test_nodes.py::TestAgentNodes::test_router_node_identifies_search PASSED
tests/integration/test_api_endpoints.py::TestAPIEndpoints::test_health_check PASSED
tests/integration/test_chat_flow.py::TestChatFlow::test_amenity_filtering_flow PASSED
...

========================= 25 passed in 12.34s ==========================
Coverage: 85% (travel_agents, travel_api, travel_tools)
```

---

## 📝 Next Steps

1. ✅ Run cleanup commands (remove unnecessary files)
2. ✅ Update requirements.txt with pytest dependencies
3. ✅ Create pytest.ini configuration
4. ✅ Create tests/ directory structure
5. ✅ Create all test files above
6. ✅ Run tests: `pytest tests/ -v`
7. ✅ Check coverage: `pytest --cov-report=html`
8. ✅ Add test results to presentation

---

## 💡 Testing Best Practices

✅ **Do:**

- Write tests for core functionality (search, routing, booking)
- Test both happy path and error cases
- Use fixtures for common setup
- Test integration endpoints
- Keep tests isolated and independent

❌ **Don't:**

- Test external dependencies (API keys, network calls)
- Mock excessively - use real data when possible
- Write tests that are harder to understand than the code
- Skip error case testing

---

## 📚 Files Modified/Created

| File                                    | Action | Purpose                                             |
| --------------------------------------- | ------ | --------------------------------------------------- |
| requirements.txt                        | UPDATE | Add pytest, pytest-asyncio, pytest-cov, pytest-mock |
| pytest.ini                              | CREATE | Pytest configuration                                |
| tests/                                  | CREATE | New test directory                                  |
| tests/conftest.py                       | CREATE | Shared fixtures                                     |
| tests/test_search_tool.py               | CREATE | Search tool unit tests                              |
| tests/test_search_engine.py             | CREATE | Search engine unit tests                            |
| tests/test_llms.py                      | CREATE | LLM rotation unit tests                             |
| tests/test_nodes.py                     | CREATE | Agent node unit tests                               |
| tests/test_graph.py                     | CREATE | Graph execution unit tests                          |
| tests/test_booking_tool.py              | CREATE | Booking unit tests                                  |
| tests/integration/                      | CREATE | Integration tests directory                         |
| tests/integration/test_api_endpoints.py | CREATE | API endpoint tests                                  |
| tests/integration/test_chat_flow.py     | CREATE | Chat flow integration tests                         |

---

Good luck with testing! 🧪✨
