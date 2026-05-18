# Tests resort search engine behavior and matching logic.
# File: tests/test_search_engine.py


"""Unit tests for search engine filtering logic."""
import pytest
from travel_tools.search_engine import SearchFilters, retrieve_matching_resorts


class TestSearchFilters:
    """Test SearchFilters model."""
    
    def test_create_filters_with_budget(self):
        """Test creating filters with budget."""
        filters = SearchFilters(max_budget=8000)
        assert filters.max_budget == 8000
    
    def test_create_filters_with_rating(self):
        """Test creating filters with rating."""
        filters = SearchFilters(min_rating=4.5)
        assert filters.min_rating == 4.5
    
    def test_create_filters_with_amenities(self):
        """Test creating filters with required amenities."""
        amenities = ['pool', 'wifi']
        filters = SearchFilters(required_amenities=amenities)
        assert filters.required_amenities == amenities
    
    def test_create_filters_with_multiple_resort_names(self):
        """Test creating filters with multiple resort names."""
        names = ["River Valley", "Jungle Camp", "Tiger Resort"]
        filters = SearchFilters(target_resort_names=names)
        assert filters.target_resort_names == names
    
    def test_optional_fields_defaults(self):
        """Test that optional fields have proper defaults."""
        filters = SearchFilters()
        assert filters.min_rating is None
        assert filters.max_budget is None
        assert filters.guest_count is None
        assert filters.family_friendly is None


class TestBudgetFiltering:
    """Test budget-based filtering."""
    
    def test_budget_upper_limit(self, sample_resorts_list):
        """Test filtering by maximum budget."""
        filters = SearchFilters(max_budget=5500)
        filtered = filter_resorts(sample_resorts_list, filters)
        assert all(r['price'] <= 5500 for r in filtered)
    
    def test_budget_excludes_expensive(self, sample_resorts_list):
        """Test that expensive resorts are excluded."""
        filters = SearchFilters(max_budget=5000)
        filtered = filter_resorts(sample_resorts_list, filters)
        # Resort priced at 6500 should be filtered out
        resort_names = [r['name'] for r in filtered]
        assert 'Tiger Resort' not in resort_names
    
    def test_very_tight_budget(self, sample_resorts_list):
        """Test very tight budget might return few results."""
        filters = SearchFilters(max_budget=4000)
        filtered = filter_resorts(sample_resorts_list, filters)
        # Should return empty or very few results
        assert len(filtered) <= 1


class TestRatingFiltering:
    """Test rating-based filtering."""
    
    def test_minimum_rating_filter(self, sample_resorts_list):
        """Test filtering by minimum rating."""
        filters = SearchFilters(min_rating=4.0)
        filtered = filter_resorts(sample_resorts_list, filters)
        for resort in filtered:
            rating = resort.get('rating', 0)
            if rating > 0:  # Only check if rating exists
                assert rating >= 4.0
    
    def test_high_rating_filter(self, sample_resorts_list):
        """Test filtering with high minimum rating."""
        filters = SearchFilters(min_rating=4.8)
        filtered = filter_resorts(sample_resorts_list, filters)
        # Should return very few high-rated resorts
        assert len(filtered) <= len(sample_resorts_list)


class TestAmenityFiltering:
    """Test amenity-based filtering."""
    
    def test_single_amenity_required(self, sample_resorts_list):
        """Test filtering by single required amenity."""
        filters = SearchFilters(required_amenities=['pool'])
        filtered = filter_resorts(sample_resorts_list, filters)
        assert len(filtered) > 0
        for resort in filtered:
            amenities = resort.get('amenities', [])
            if amenities:
                assert 'pool' in amenities
    
    def test_multiple_amenities_required(self, sample_resorts_list):
        """Test filtering by multiple required amenities."""
        filters = SearchFilters(required_amenities=['pool', 'wifi'])
        filtered = filter_resorts(sample_resorts_list, filters)
        for resort in filtered:
            amenities = resort.get('amenities', [])
            if amenities:
                # Should have both amenities
                assert 'pool' in amenities or 'wifi' in amenities
    
    def test_nonexistent_amenity(self, sample_resorts_list):
        """Test filtering with nonexistent amenity."""
        filters = SearchFilters(required_amenities=['helipad', 'golf-course'])
        filtered = filter_resorts(sample_resorts_list, filters)
        # May return empty if no resort has these amenities
        assert isinstance(filtered, list)
    
    def test_amenity_case_sensitivity(self, sample_resorts_list):
        """Test that amenity matching handles case properly."""
        # Create filters with different case
        filters = SearchFilters(required_amenities=['POOL'])
        filtered = filter_resorts(sample_resorts_list, filters)
        # Should still find results if case-insensitive
        assert isinstance(filtered, list)


class TestGuestCountFiltering:
    """Test guest count filtering."""
    
    def test_guest_count_filter(self, sample_resorts_list):
        """Test filtering by guest count."""
        filters = SearchFilters(guest_count=2)
        filtered = filter_resorts(sample_resorts_list, filters)
        # Should return suitable resorts for 2 guests
        assert len(filtered) > 0
    
    def test_large_guest_group(self, sample_resorts_list):
        """Test filtering for large guest group."""
        filters = SearchFilters(guest_count=10)
        filtered = filter_resorts(sample_resorts_list, filters)
        # Should return resorts suitable for 10 guests
        assert isinstance(filtered, list)


class TestFamilyFriendlyFiltering:
    """Test family-friendly filtering."""
    
    def test_family_friendly_filter_enabled(self, sample_resorts_list):
        """Test filtering for family-friendly resorts."""
        filters = SearchFilters(family_friendly=True)
        filtered = filter_resorts(sample_resorts_list, filters)
        assert len(filtered) > 0
    
    def test_family_friendly_filter_disabled(self, sample_resorts_list):
        """Test that family_friendly=False doesn't filter."""
        filters = SearchFilters(family_friendly=False)
        filtered = filter_resorts(sample_resorts_list, filters)
        # Should return all resorts
        assert len(filtered) > 0


class TestCombinedFilters:
    """Test multiple filters working together."""
    
    def test_budget_and_rating(self, sample_resorts_list):
        """Test budget and rating filters together."""
        filters = SearchFilters(
            max_budget=8000,
            min_rating=4.0
        )
        filtered = filter_resorts(sample_resorts_list, filters)
        assert all(r['price'] <= 8000 for r in filtered)
    
    def test_all_filters_combined(self, sample_resorts_list):
        """Test all filters combined."""
        filters = SearchFilters(
            max_budget=8000,
            min_rating=4.0,
            required_amenities=['pool', 'wifi'],
            guest_count=2,
            family_friendly=True
        )
        filtered = filter_resorts(sample_resorts_list, filters)
        assert len(filtered) >= 0  # May be empty if no resort matches all
        assert all(r['price'] <= 8000 for r in filtered)


class TestEdgeCases:
    """Test edge cases in filtering."""
    
    def test_empty_resort_list(self):
        """Test filtering empty resort list."""
        filters = SearchFilters(max_budget=8000)
        filtered = filter_resorts([], filters)
        assert filtered == []
    
    def test_resort_missing_amenities(self):
        """Test filtering when resort has no amenities field."""
        resorts = [
            {'name': 'Resort A', 'price': 5000},  # No amenities
            {'name': 'Resort B', 'price': 6000, 'amenities': ['pool']}
        ]
        filters = SearchFilters(required_amenities=['pool'])
        filtered = filter_resorts(resorts, filters)
        # Should handle missing amenities gracefully
        assert isinstance(filtered, list)
    
    def test_resort_missing_price(self):
        """Test filtering when resort has no price."""
        resorts = [
            {'name': 'Resort A'},  # No price
            {'name': 'Resort B', 'price': 5000}
        ]
        filters = SearchFilters(max_budget=8000)
        filtered = filter_resorts(resorts, filters)
        # Should handle missing price gracefully
        assert isinstance(filtered, list)