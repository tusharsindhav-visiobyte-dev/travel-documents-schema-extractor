"""Serialization, JSON Schema, and example document tests."""

import json
from pathlib import Path

import pytest

from events.event_schema import TravelEventSchema
from registry.schema_registry import export_json_schema, get_schema, get_supported_document_types
from validation.schema_validator import generate_json_schema, serialize_model, serialize_model_json

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"

EXAMPLE_FILES = {
    "flight_ticket.json": "flight_ticket",
    "hotel_booking.json": "hotel_booking",
    "train_ticket.json": "train_ticket",
    "bus_ticket.json": "bus_ticket",
    "car_rental.json": "car_rental",
    "travel_itinerary.json": "travel_itinerary",
    "passport.json": "passport",
    "travel_insurance.json": "travel_insurance",
    "cruise_booking.json": "cruise_booking",
    "tour_booking.json": "tour_booking",
    "airport_transfer.json": "airport_transfer",
    "travel_invoice.json": "travel_invoice",
    "corporate_travel_authorization.json": "corporate_travel_authorization",
    "child_travel_consent.json": "child_travel_consent",
}


@pytest.mark.parametrize("document_type", get_supported_document_types())
def test_every_registered_schema_serializes_and_exports_json_schema(document_type: str):
    schema = get_schema(document_type)
    model = schema()
    payload = serialize_model(model)
    assert payload["document_type"] == document_type
    assert payload["schema_version"] == "1.0.0"
    restored = schema.model_validate_json(serialize_model_json(model))
    assert restored == model

    json_schema = export_json_schema(document_type)
    assert json_schema["type"] == "object"
    assert json_schema["properties"]["document_type"]["const"] == document_type
    assert generate_json_schema(schema)["title"] == schema.__name__


def test_event_schema_serializes_and_exports_json_schema():
    event = TravelEventSchema(event_type="visa_expiry", title="Visa expires")
    restored = TravelEventSchema.model_validate_json(serialize_model_json(event))
    assert restored == event
    json_schema = generate_json_schema(TravelEventSchema)
    assert json_schema["type"] == "object"
    assert "event_type" in json_schema["properties"]
    assert "event_type" in json_schema["required"]


@pytest.mark.parametrize("filename,document_type", EXAMPLE_FILES.items())
def test_example_files_validate_and_round_trip(filename: str, document_type: str):
    payload = json.loads((EXAMPLES / filename).read_text(encoding="utf-8"))
    assert payload["document_type"] == document_type
    schema = get_schema(document_type)
    model = schema.model_validate(payload)
    restored = schema.model_validate(serialize_model(model))
    assert restored == model
    json_schema = export_json_schema(document_type)
    assert isinstance(json_schema, dict)
    assert json_schema["properties"]


def test_flight_example_has_multiple_passengers_and_segments():
    payload = json.loads((EXAMPLES / "flight_ticket.json").read_text(encoding="utf-8"))
    model = get_schema("flight_ticket").model_validate(payload)
    assert len(model.passengers) == 2
    assert len(model.segments) == 2
    assert model.segments[0].departure.iana_timezone != model.segments[0].arrival.iana_timezone
    assert model.extraction_metadata.evidence[0].confidence == 0.74


def test_hotel_example_has_multiple_guests():
    payload = json.loads((EXAMPLES / "hotel_booking.json").read_text(encoding="utf-8"))
    model = get_schema("hotel_booking").model_validate(payload)
    assert len(model.guests) == 2
    assert len(model.rooms) == 2
    assert model.number_of_nights == 3


def test_itinerary_example_has_multiple_days_and_destinations():
    payload = json.loads((EXAMPLES / "travel_itinerary.json").read_text(encoding="utf-8"))
    model = get_schema("travel_itinerary").model_validate(payload)
    assert len(model.destinations) >= 2
    assert len(model.days) >= 3


def test_date_serializes_as_iso_and_original_text_remains():
    schema = get_schema("flight_ticket")
    model = schema.model_validate(
        {
            "issue_date": {
                "original_date": "02 Nov 2026",
                "normalized_date": "2026-11-02",
                "date_only": True,
            }
        }
    )
    payload = serialize_model(model, exclude_none=True)
    assert payload["issue_date"]["normalized_date"] == "2026-11-02"
    assert payload["issue_date"]["original_date"] == "02 Nov 2026"
