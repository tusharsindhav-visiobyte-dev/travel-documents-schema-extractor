"""Tests for specialized documents, events, and business rules."""

import pytest
from pydantic import ValidationError

from events.event_schema import TravelEventSchema
from events.event_types import EventType
from registry.schema_registry import get_schema, validate_document_type
from schemas.flight import (
    FlightBoardingPassSchema,
    FlightBookingConfirmationSchema,
    FlightTicketSchema,
)
from schemas.hotel import HotelBookingSchema
from schemas.identity import PassportSchema
from schemas.itinerary import TravelItinerarySchema
from validation.business_rules import (
    BusinessFinding,
    register_business_rule,
    reset_custom_business_rules,
    run_business_rules,
)
from validation.schema_validator import validate_document, validate_model


def test_flight_ticket_supports_multiple_passengers_and_segments():
    ticket = FlightTicketSchema.model_validate(
        {
            "pnr": "HX4Q2P",
            "passengers": [
                {"name": {"original_name": "Ada Lovelace"}, "ticket_number": "098111"},
                {"name": {"original_name": "Grace Hopper"}, "ticket_number": "098222"},
            ],
            "segments": [
                {
                    "segment_id": "seg-1",
                    "flight_number": "EX101",
                    "departure_airport": {"iata_code": "LHR", "name": "London Heathrow"},
                    "departure": {"iana_timezone": "Europe/London", "original_date": "15 Nov 2026"},
                    "arrival": {"iana_timezone": "Asia/Kolkata", "original_date": "16 Nov 2026"},
                    "overnight_journey": True,
                },
                {
                    "segment_id": "seg-2",
                    "flight_number": "EX202",
                    "departure": {"iana_timezone": "Asia/Kolkata"},
                    "arrival": {"iana_timezone": "Asia/Kolkata"},
                },
            ],
            "ticket_numbers": ["098111", "098222"],
        }
    )
    assert len(ticket.passengers) == 2
    assert len(ticket.segments) == 2
    assert ticket.segments[0].departure.iana_timezone != ticket.segments[0].arrival.iana_timezone


def test_ticket_confirmation_and_boarding_pass_are_different_schemas():
    assert FlightTicketSchema is not FlightBookingConfirmationSchema
    assert FlightBookingConfirmationSchema is not FlightBoardingPassSchema
    assert FlightTicketSchema().document_type == "flight_ticket"
    assert FlightBookingConfirmationSchema().document_type == "flight_booking_confirmation"
    assert FlightBoardingPassSchema().document_type == "flight_boarding_pass"
    assert "ticketing_deadline" in FlightBookingConfirmationSchema.model_fields
    assert "boarding_time" in FlightBoardingPassSchema.model_fields
    assert "ticket_numbers" in FlightTicketSchema.model_fields


def test_flight_ticket_allows_null_and_rejects_wrong_types_without_losing_valid_fields():
    ticket = FlightTicketSchema(pnr=None, passengers=None, segments=None)
    assert ticket.pnr is None
    result = validate_model(
        FlightTicketSchema,
        {"pnr": 12345, "language": "en", "segments": [{"flight_number": "EX101"}]},
    )
    assert result.valid is False
    assert result.partial_model is not None
    assert result.partial_model.language == "en"
    assert result.partial_model.segments[0].flight_number == "EX101"
    assert any(error.field_path == "pnr" for error in result.errors)


def test_invalid_nested_timezone_keeps_the_rest_of_the_segment():
    result = validate_document(
        "flight_ticket",
        {
            "pnr": "ABC123",
            "segments": [
                {
                    "flight_number": "EX101",
                    "departure": {"original_date": "15 Nov 2026", "iana_timezone": "Not/AZone"},
                }
            ],
        },
    )
    assert result.valid is False
    assert result.partial_model.pnr == "ABC123"
    assert result.partial_model.segments[0].flight_number == "EX101"
    assert result.partial_model.segments[0].departure.original_date == "15 Nov 2026"
    assert result.partial_model.segments[0].departure.iana_timezone is None
    assert result.preserved_data["pnr"] == "ABC123"


def test_hotel_booking_supports_multiple_guests_and_does_not_invent_nights():
    booking = HotelBookingSchema.model_validate(
        {
            "guest_count": 2,
            "guests": [
                {"name": {"original_name": "Ada Lovelace"}, "is_primary_guest": True},
                {"name": {"original_name": "Grace Hopper"}},
            ],
            "rooms": [
                {"room_type": "deluxe", "room_quantity": 1},
                {"room_type": "suite", "room_quantity": 1},
            ],
            "check_in": {
                "normalized_date": "2026-11-10",
                "iana_timezone": "Europe/Paris",
                "time_unknown": True,
            },
            "check_out": {
                "normalized_date": "2026-11-13",
                "iana_timezone": "Europe/Paris",
                "time_unknown": True,
            },
        }
    )
    assert len(booking.guests) == 2
    assert len(booking.rooms) == 2
    assert booking.number_of_nights is None
    assert booking.check_in.iana_timezone == "Europe/Paris"
    assert run_business_rules(booking) == []


def test_night_count_mismatch_is_reported_and_kept():
    booking = HotelBookingSchema.model_validate(
        {
            "number_of_nights": 1,
            "check_in": {"normalized_date": "2026-11-10"},
            "check_out": {"normalized_date": "2026-11-13"},
        }
    )
    findings = run_business_rules(booking)
    assert any(item.code == "night_count_mismatch" for item in findings)
    assert booking.number_of_nights == 1


def test_unknown_timezones_are_not_used_to_order_a_journey():
    ticket = FlightTicketSchema.model_validate(
        {
            "segments": [
                {
                    "departure": {"local_datetime": "2026-11-16T22:00:00", "timezone_known": False},
                    "arrival": {"local_datetime": "2026-11-16T18:00:00", "timezone_known": False},
                }
            ]
        }
    )
    assert run_business_rules(ticket) == []


def test_known_utc_instants_report_an_arrival_before_departure():
    ticket = FlightTicketSchema.model_validate(
        {
            "segments": [
                {
                    "departure": {"utc_datetime": "2026-11-16T10:00:00Z"},
                    "arrival": {"utc_datetime": "2026-11-16T08:00:00Z"},
                }
            ]
        }
    )
    findings = run_business_rules(ticket)
    assert findings[0].code == "interval_ends_before_start"
    assert findings[0].severity == "warning"
    assert ticket.segments[0].arrival.utc_datetime < ticket.segments[0].departure.utc_datetime


def test_itinerary_supports_multiple_days_and_destinations():
    itinerary = TravelItinerarySchema.model_validate(
        {
            "trip_name": "Paris and Lyon",
            "destinations": [{"name": "Paris"}, {"name": "Lyon"}],
            "days": [
                {"day_number": 1, "title": "Arrive", "locations": [{"name": "Paris"}]},
                {"day_number": 2, "title": "Museums", "activities": [{"title": "Louvre"}]},
                {"day_number": 3, "title": "Travel", "transportation": [{"mode": "train"}]},
            ],
        }
    )
    assert len(itinerary.destinations) == 2
    assert len(itinerary.days) == 3
    assert itinerary.days[2].transportation[0].mode == "train"


def test_passport_is_valid_without_sensitive_numbers():
    passport = PassportSchema(
        issuing_country="Exampleland",
        nationality=None,
        identity_document_number=None,
        holder={"name": {"original_name": "Ada Lovelace"}},
    )
    assert passport.identity_document_number is None
    assert passport.document_type == "passport"


def test_travel_event_is_not_a_document_type():
    assert validate_document_type("flight_departure") is False
    with pytest.raises(ValidationError):
        TravelEventSchema()
    event = TravelEventSchema(
        event_type=EventType.FLIGHT_DEPARTURE,
        title="Leave London",
        source_document_ids=["doc-flight-1001"],
        traveler_ids=["trv-1", "trv-2"],
        start_datetime={"iana_timezone": "Europe/London", "original_time": "21:30"},
        location={"name": "London Heathrow"},
        destination={"name": "Delhi"},
    )
    assert event.event_type == "flight_departure"
    assert get_schema("flight_ticket") is not TravelEventSchema


def test_custom_business_rule_hook_does_not_change_data():
    class NeedsPnr:
        code = "needs_pnr"

        def evaluate(self, model):
            if getattr(model, "DOCUMENT_TYPE", None) == "flight_ticket" and model.pnr is None:
                return [BusinessFinding(code=self.code, message="PNR was not printed.", field_path="pnr")]
            return []

    register_business_rule(NeedsPnr(), {"flight_ticket"})
    try:
        ticket = FlightTicketSchema(language="en")
        findings = run_business_rules(ticket)
        assert any(item.code == "needs_pnr" for item in findings)
        assert ticket.language == "en"
        assert ticket.pnr is None
    finally:
        reset_custom_business_rules()


def test_validation_result_for_a_valid_document_has_no_errors():
    result = validate_document("train_ticket", {"pnr": "4529183746", "train_number": "12259"})
    assert result.valid is True
    assert result.errors == []
    assert result.model.pnr == "4529183746"
    assert result.preserved_data["train_number"] == "12259"
