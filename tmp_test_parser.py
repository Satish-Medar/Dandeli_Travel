# Temporary parser proof-of-concept used for validating date parsing logic.
# File: tmp_test_parser.py


from travel_agents.nodes import parse_booking_dates_from_text
print(parse_booking_dates_from_text('Check-in May 15 and check-out May 17, 2026'))