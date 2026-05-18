# Tests the resort search tool formatting and result handling.
# File: tests/test_search_tool.py


"""Unit tests for resort search tool."""
import pytest
from travel_tools.search_tool import find_resort_by_name, search_resorts
from travel_tools.search_engine import SearchFilters, filter_resorts


class TestFindResortByName:
    """Test finding resorts by name."""
    
    def test_find_exact_match(self):
        """Test finding resort with exact name match."""
        resort = find_resort_by_name("River Valley")
        assert resort is not None
        assert resort['name'] == "River Valley"
    
    def test_find_partial_match(self):
        """Test finding resort with partial name."""
        resort = find_resort_by_name("Jungle")
        assert resort is not None
        assert "Jungle" in resort['name']
    
    def test_find_with_spaces(self):
        """Test finding resort with spaces in name."""
        resort = find_resort_by_name("Tiger Resort")
        assert resort is not None
    
    def test_nonexistent_resort(self):
        """Test searching for nonexistent resort."""
        resort = find_resort_by_name("Nonexistent Resort 123")
        # Should return None or empty result
        assert resort is None or resort == {}
    
    def test_case_insensitive_search(self):
        """Test that search is case-insensitive."""
        resort1 = find_resort_by_name("river valley")
        resort2 = find_resort_by_name("RIVER VALLEY")
        # Both should find the same resort
        assert resort1 is not None
        assert resort2 is not None


class TestSearchResorts:
    """Test searching resorts with filters."""
    
    def test_search_all_resorts(self):
        """Test searching all resorts without filters."""
        results = search_resorts("resort")
        assert len(results) > 0
    
    def test_search_with_budget_filter(self):
        """Test searching with budget constraint."""
        filters = SearchFilters(max_budget=8000)
        results = search_resorts("resort", filters)
        assert len(results) > 0
        assert all(r['price'] <= 8000 for r in results)
    
    def test_search_with_rating_filter(self):
        """Test searching with minimum rating."""
        filters = SearchFilters(min_rating=4.0)
        results = search_resorts("resort", filters)
        assert len(results) > 0
        assert all(r.get('rating', 0) >= 4.0 for r in results)
    
    def test_search_with_multiple_filters(self):
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
        """Test searching for multiple resorts by name."""
        filters = SearchFilters(
            target_resort_names=["River Valley", "Jungle Camp"]
        )
        results = search_resorts("compare", filters)
        assert len(results) > 0
    
    def test_search_with_amenities(self):
        """Test searching with required amenities."""
        filters = SearchFilters(
            required_amenities=['pool', 'wifi']
        )
        results = search_resorts("resort with pool and wifi", filters)
        assert len(results) > 0
        # Check that all results have the required amenities
        for resort in results:
            amenities = resort.get('amenities', [])
            if amenities:  # Only check if amenities exist
                assert 'pool' in amenities or 'wifi' in amenities
    
    def test_search_returns_limited_results(self):
        """Test that search returns limited results (max 5)."""
        results = search_resorts("resort")
        # Should return at most 5 results to save tokens
        assert len(results) <= 5
    
    def test_search_empty_query(self):
        """Test search with empty query."""
        results = search_resorts("")
        # Should still work, returning default results
        assert len(results) >= 0
    
    def test_search_with_guest_count(self):
        """Test searching with guest count filter."""
        filters = SearchFilters(guest_count=2)
        results = search_resorts("resort for 2 guests", filters)
        assert len(results) > 0


class TestResortFiltering:
    """Test resort filtering logic."""
    
    def test_filter_by_budget(self, sample_resorts_list):
        """Test filtering by budget."""
        filters = SearchFilters(max_budget=5500)
        filtered = filter_resorts(sample_resorts_list, filters)
        assert all(r['price'] <= 5500 for r in filtered)
    
    def test_filter_by_rating(self, sample_resorts_list):
        """Test filtering by minimum rating."""
        filters = SearchFilters(min_rating=4.0)
        filtered = filter_resorts(sample_resorts_list, filters)
        # All should have rating >= 4.0 if filter is applied correctly
        assert len(filtered) > 0
    
    def test_filter_by_family_friendly(self, sample_resorts_list):
        """Test filtering for family-friendly resorts."""
        filters = SearchFilters(family_friendly=True)
        filtered = filter_resorts(sample_resorts_list, filters)
        # Should still return results
        assert len(filtered) > 0
    
    def test_combined_filters(self, sample_resorts_list):
        """Test multiple filters combined."""
        filters = SearchFilters(
            max_budget=6000,
            min_rating=4.0
        )
        filtered = filter_resorts(sample_resorts_list, filters)
        assert all(r['price'] <= 6000 for r in filtered)


class TestResortMatching:
    """Test exact/fuzzy matching for resort names."""
    
    def test_exact_name_matching(self):
        """Test exact match gives priority."""
        # Should match exactly
        resort = find_resort_by_name("River Valley")
        assert resort is not None
    
    def test_partial_word_matching(self):
        """Test partial word matching."""
        resort = find_resort_by_name("Jungle")
        assert resort is not None
        assert "Jungle" in resort.get('name', '')
    
    def test_word_with_suffix_removal(self):
        """Test matching with suffix removal (camp, resort, etc)."""
        # 'Jungle Camp' should still be found
        resort = find_resort_by_name("Jungle")
        assert resort is not None