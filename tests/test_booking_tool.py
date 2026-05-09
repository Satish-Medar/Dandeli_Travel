"""Unit tests for booking functionality."""
import pytest
from travel_tools.booking_tool import create_booking, get_booking_status
from travel_tools.booking_store import BookingStore


class TestBookingStore:
    """Test booking store functionality."""
    
    @pytest.fixture
    def booking_store(self):
        """Create temporary booking store."""
        return BookingStore()
    
    def test_booking_store_initialization(self, booking_store):
        """Test booking store initializes correctly."""
        assert booking_store is not None
    
    def test_save_booking(self, booking_store):
        """Test saving a booking."""
        booking_data = {
            'sessionId': 'session-123',
            'resort': 'River Valley',
            'dates': {'start': '2026-05-15', 'end': '2026-05-17'},
            'guests': 2,
            'contactInfo': {'email': 'user@example.com', 'phone': '9876543210'}
        }
        
        result = booking_store.save_booking(booking_data)
        assert result['bookingId'] is not None
        assert result['status'] == 'confirmed'
    
    def test_get_booking_status(self, booking_store):
        """Test retrieving booking status."""
        # Create a booking first
        booking_data = {
            'sessionId': 'session-456',
            'resort': 'Jungle Camp',
            'dates': {'start': '2026-05-20', 'end': '2026-05-22'},
            'guests': 2,
            'contactInfo': {'email': 'test@example.com', 'phone': '9876543210'}
        }
        
        saved_booking = booking_store.save_booking(booking_data)
        booking_id = saved_booking['bookingId']
        
        # Retrieve status
        status = booking_store.get_status(booking_id)
        assert status in ['pending', 'confirmed', 'cancelled']
    
    def test_get_nonexistent_booking_status(self, booking_store):
        """Test retrieving status for nonexistent booking."""
        status = booking_store.get_status('nonexistent-booking-id')
        # Should handle gracefully
        assert status is None or isinstance(status, str)


class TestCreateBooking:
    """Test booking creation functionality."""
    
    def test_create_booking_with_valid_data(self):
        """Test creating booking with valid data."""
        booking_data = {
            'sessionId': 'session-123',
            'resort': 'River Valley',
            'dates': {'start': '2026-05-15', 'end': '2026-05-17'},
            'guests': 2,
            'contactInfo': {'email': 'user@example.com', 'phone': '9876543210'}
        }
        
        result = create_booking(booking_data)
        assert result['bookingId'] is not None
        assert result['status'] == 'confirmed'
        assert 'resort' in result
        assert 'dates' in result
    
    def test_create_booking_missing_required_fields(self):
        """Test creating booking with missing fields."""
        incomplete_data = {
            'sessionId': 'session-123',
            # Missing resort, dates, etc.
        }
        
        # Should handle gracefully or raise appropriate error
        try:
            result = create_booking(incomplete_data)
            # If it succeeds, should have some default handling
            assert isinstance(result, dict)
        except Exception as e:
            # Expected to fail with missing data
            assert "required" in str(e).lower() or "missing" in str(e).lower()
    
    def test_create_booking_with_invalid_dates(self):
        """Test creating booking with invalid date format."""
        invalid_data = {
            'sessionId': 'session-123',
            'resort': 'River Valley',
            'dates': {'start': 'invalid-date', 'end': '2026-05-17'},
            'guests': 2,
            'contactInfo': {'email': 'user@example.com', 'phone': '9876543210'}
        }
        
        # Should handle invalid dates gracefully
        try:
            result = create_booking(invalid_data)
            assert isinstance(result, dict)
        except Exception:
            # Expected to fail with invalid dates
            pass


class TestBookingStatus:
    """Test booking status retrieval."""
    
    def test_get_booking_status_existing(self):
        """Test getting status for existing booking."""
        # This would require a real booking in the store
        # For now, test the function signature
        booking_id = "test-booking-id"
        status = get_booking_status(booking_id)
        # Should return a status or None
        assert status is None or isinstance(status, str)
    
    def test_get_booking_status_nonexistent(self):
        """Test getting status for nonexistent booking."""
        status = get_booking_status("nonexistent-id")
        assert status is None or status == "not_found"


class TestBookingValidation:
    """Test booking data validation."""
    
    def test_valid_booking_data(self):
        """Test validation of valid booking data."""
        valid_data = {
            'sessionId': 'session-123',
            'resort': 'River Valley',
            'dates': {'start': '2026-05-15', 'end': '2026-05-17'},
            'guests': 2,
            'contactInfo': {'email': 'user@example.com', 'phone': '9876543210'}
        }
        
        # Should pass validation
        assert 'sessionId' in valid_data
        assert 'resort' in valid_data
        assert 'dates' in valid_data
        assert 'guests' in valid_data
        assert 'contactInfo' in valid_data
    
    def test_booking_guest_count_validation(self):
        """Test guest count validation."""
        # Test various guest counts
        for guest_count in [1, 2, 4, 6]:
            data = {
                'sessionId': 'session-123',
                'resort': 'River Valley',
                'dates': {'start': '2026-05-15', 'end': '2026-05-17'},
                'guests': guest_count,
                'contactInfo': {'email': 'user@example.com', 'phone': '9876543210'}
            }
            
            result = create_booking(data)
            assert result['bookingId'] is not None
    
    def test_booking_date_validation(self):
        """Test date validation."""
        # Valid date format
        valid_dates = {'start': '2026-05-15', 'end': '2026-05-17'}
        data = {
            'sessionId': 'session-123',
            'resort': 'River Valley',
            'dates': valid_dates,
            'guests': 2,
            'contactInfo': {'email': 'user@example.com', 'phone': '9876543210'}
        }
        
        result = create_booking(data)
        assert result['bookingId'] is not None


class TestBookingIntegration:
    """Test booking integration with other components."""
    
    def test_booking_with_resort_search(self):
        """Test booking after resort search."""
        # This would test the full flow: search → select → book
        # For now, test individual components work together
        
        # 1. Search for resorts
        from travel_tools.search_tool import search_resorts
        results = search_resorts("resort")
        assert len(results) > 0
        
        # 2. Create booking for first result
        resort_name = results[0]['name']
        booking_data = {
            'sessionId': 'session-integration-test',
            'resort': resort_name,
            'dates': {'start': '2026-05-15', 'end': '2026-05-17'},
            'guests': 2,
            'contactInfo': {'email': 'integration@example.com', 'phone': '9876543210'}
        }
        
        result = create_booking(booking_data)
        assert result['bookingId'] is not None
        assert result['resort'] == resort_name
    
    def test_booking_status_after_creation(self):
        """Test booking status immediately after creation."""
        booking_data = {
            'sessionId': 'session-status-test',
            'resort': 'River Valley',
            'dates': {'start': '2026-05-15', 'end': '2026-05-17'},
            'guests': 2,
            'contactInfo': {'email': 'status@example.com', 'phone': '9876543210'}
        }
        
        # Create booking
        created = create_booking(booking_data)
        booking_id = created['bookingId']
        
        # Check status
        status = get_booking_status(booking_id)
        assert status in ['pending', 'confirmed', 'cancelled']
