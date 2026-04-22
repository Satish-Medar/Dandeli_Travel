from langchain_core.tools import tool

from .booking_store import load_bookings
from .search_engine import clean_text


@tool
def get_booking_status(booking_id: str) -> str:
    """Look up the current booking status using a booking ID like BK-0001."""
    for booking in load_bookings():
        if booking.get("booking_id", "").lower() == booking_id.lower():
            return f"Booking ID: {booking['booking_id']}\nResort: {booking['resort_name']}\nDates: {clean_text(str(booking['check_in_out_dates']).title())}\nGuests: {clean_text(booking['guest_details'])}\nStatus: {booking['status']}\nCreated: {booking['created_at']}\nTwilio Status: {booking.get('twilio_status', 'unknown')}\nTwilio SID: {booking.get('twilio_message_sid', 'N/A')}\nTwilio Error: {booking.get('twilio_error_message') or booking.get('twilio_error_code') or 'None'}"
    return "I could not find a booking with that ID. Please check the booking ID and try again."
