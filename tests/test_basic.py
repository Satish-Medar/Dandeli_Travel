"""Simple test to verify testing setup works."""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_basic_import():
    """Test that we can import our modules."""
    try:
        from travel_tools.search_engine import SearchFilters
        filters = SearchFilters(max_budget=8000)
        assert filters.max_budget == 8000
        print("✅ Basic import test passed")
    except Exception as e:
        print(f"❌ Basic import test failed: {e}")
        raise

def test_pytest_setup():
    """Test that pytest is working."""
    assert True  # This should always pass
    print("✅ Pytest setup test passed")

if __name__ == "__main__":
    test_basic_import()
    test_pytest_setup()
    print("🎉 All basic tests passed!")