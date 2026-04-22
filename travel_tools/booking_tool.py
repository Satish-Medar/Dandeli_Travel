import os
from datetime import datetime
from time import sleep

from langchain_core.tools import tool
from twilio.rest import Client

from .booking_store import load_bookings, next_booking_id, save_bookings
from .search_engine import clean_text


def _format_whatsapp_endpoint(number: str) -> str:
    normalized = number.strip()
    return normalized if normalized.lower().startswith("whatsapp:") else f"whatsapp:{normalized}"


@tool
def book_resort(resort_name: str, check_in_out_dates: str, guest_details: str, customer_contact: str) -> str:
    """Send a booking request via WhatsApp to the owner. `check_in_out_dates` must be exact calendar dates."""
    credentials = [os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"), os.getenv("TWILIO_PHONE_NUMBER"), os.getenv("DESTINATION_PHONE_NUMBER")]
    if not all(credentials):
        return "Missing Twilio credentials. Cannot complete booking."
    try:
        bookings = load_bookings()
        booking_id = next_booking_id(bookings)
        client = Client(credentials[0], credentials[1])
        message = client.messages.create(from_=_format_whatsapp_endpoint(credentials[2]), body=f"New Booking Request\nBooking ID: {booking_id}\nResort: {resort_name}\nDates: {check_in_out_dates}\nGuests: {guest_details}\nCustomer Contact: {customer_contact}\n\nPlease arrange payment with the customer directly.", to=_format_whatsapp_endpoint(credentials[3]))
        sleep(2)
        message_status = client.messages(message.sid).fetch()
        delivery_status = getattr(message_status, "status", "unknown")
        error_code = getattr(message_status, "error_code", None)
        error_message = getattr(message_status, "error_message", None)
        bookings.append({"booking_id": booking_id, "resort_name": resort_name, "check_in_out_dates": check_in_out_dates, "guest_details": guest_details, "customer_contact": customer_contact, "status": "requested", "created_at": datetime.now().isoformat(timespec="seconds"), "twilio_message_sid": message.sid, "twilio_status": delivery_status, "twilio_error_code": error_code, "twilio_error_message": error_message})
        save_bookings(bookings)
        if error_code or delivery_status in {"failed", "undelivered"}:
            return f"Booking request created, but WhatsApp delivery did not complete.\nBooking ID: {booking_id}\nResort: {clean_text(resort_name)}\nDates: {clean_text(check_in_out_dates.title())}\nGuests: {clean_text(guest_details)}\nTwilio Status: {delivery_status}\nTwilio SID: {message.sid}\nTwilio Error: {error_message or error_code or 'Unknown error'}"
        return f"Your booking request has been sent.\nBooking ID: {booking_id}\nResort: {clean_text(resort_name)}\nDates: {clean_text(check_in_out_dates.title())}\nGuests: {clean_text(guest_details)}\n\nTwilio Status: {delivery_status}\nThe resort owner has been notified on WhatsApp and should respond soon."
    except Exception as error:
        return f"Failed to send booking request via WhatsApp: {error}"
