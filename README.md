# Travel Document Schema

A Python schema system for travel documents. It defines the shared data model, one specialized schema per document type, a versioned registry, and validation that can keep the fields which did parse.

The schema packages define and validate documents. They do not read files or call a model. The `api` package classifies pasted text or an uploaded file into one registered document type.

## Layers

**Universal base.** Every document schema extends `BaseDocumentSchema`. The shared record carries document identity, issuer, status, language, trip context, traveler and related-document links, extraction evidence, provider extensions, and original text.

**Shared components.** People, travelers, passengers, guests, providers, places, airports, stations, bookings, payments, dates, timezones, transport, accommodation, insurance, vehicles, routes, cancellation terms, and evidence are defined once and reused.

**Specialized documents.** A flight ticket, a booking confirmation, and a boarding pass are different schemas. The same separation is used for hotel vouchers and invoices, rail reservations and tickets, and the other document families. Category bases hold the fields those documents share. Each registered schema fixes its own `document_type`.

**Travel events.** `TravelEventSchema` is a timeline activity derived from one or more documents, such as `flight_departure` or `hotel_checkin`. It is not a document schema and it is not registered as one. This package does not generate events from documents.

## Install and test

Python 3.11 or newer and Pydantic 2.9 or newer are required.

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

## Classify a document

`POST /document-type` reads pasted text or an uploaded text file or PDF and returns one registered document type. Classification uses the Ollama model named in `.env` (`ollama_url` and `LLM_MODEL`). The model must choose an identifier from the schema registry, such as `flight_ticket` or `hotel_booking`. [How the classifier works](docs/classifier.md) describes the two model calls and the registry check.

```bash
uvicorn api.app:app --reload
```

```bash
curl -s localhost:8000/document-type \
  -H 'content-type: application/json' \
  -d '{"text":"E-TICKET\nPNR HX4Q2P\nFlight EX101"}'

curl -s localhost:8000/document-type -F 'file=@ticket.pdf'
curl -s localhost:8000/document-type -F 'text=Hotel voucher. Check-in 15 Nov 2026.'
```

```json
{"document_type": "flight_ticket"}
```

Send JSON `{"text": "..."}`, form data with `text`, or a multipart `file`. When a file and text are both present, the file is classified. A missing document, an unsupported file, an unregistered model answer, and an unreachable model return 400, 415, 422, and 502.

## Validate a document

```python
from registry import get_schema, export_json_schema
from validation import validate_document, serialize_model

result = validate_document(
    "flight_ticket",
    {
        "pnr": "HX4Q2P",
        "segments": [
            {
                "flight_number": "EX101",
                "departure": {
                    "original_date": "15 Nov 2026",
                    "iana_timezone": "Europe/London",
                    "timezone_known": True,
                },
                "arrival": {
                    "original_date": "16 Nov 2026",
                    "iana_timezone": "Asia/Kolkata",
                    "timezone_known": True,
                },
            }
        ],
    },
)

ticket = result.model
payload = serialize_model(ticket)
json_schema = export_json_schema("flight_ticket")
```

`result.valid` means the payload satisfied the schema. Business findings are a separate list and do not delete fields.

Most business fields are optional. A passport without a number, a ticket without a gate, and a hotel stay without a check-in time are valid. Supply a value only when the document shows it.

Wrong types and unknown keys are rejected. `validate_document` still returns `preserved_data` and, when the remaining fields can form a model, `partial_model`. Only the invalid leaf or list item is removed. In the example below the PNR and the printed date stay, and the unknown timezone is reported:

```python
result = validate_document(
    "flight_ticket",
    {
        "pnr": "ABC123",
        "segments": [
            {
                "flight_number": "EX101",
                "departure": {
                    "original_date": "15 Nov 2026",
                    "iana_timezone": "Not/AZone",
                },
            }
        ],
    },
)
```

## Registry

```python
from registry import (
    get_schema,
    get_schema_metadata,
    get_schema_version,
    get_supported_document_types,
    register_schema,
    validate_document_type,
)

get_schema("hotel_booking")
get_schema_version("hotel_booking")          # "1.0.0"
validate_document_type("hotel_booking")      # True
metadata = get_schema_metadata("hotel_booking")
metadata.required_fields
metadata.optional_fields
metadata.field_descriptions["check_in"]
```

`get_schema` raises `UnknownDocumentTypeError` for an identifier that was never registered, and `SchemaVersionNotFoundError` when the type exists but the version does not. Registering the same type and version again raises `DuplicateSchemaRegistrationError` unless `override=True`.

`get_schema_metadata` includes nested paths. A list of models uses `[]`, for example `segments[].flight_number`. A field is required only when the caller must send it. On a specialized document, `document_type` has a fixed default, so it is not required in the payload. On `BaseDocumentSchema` it is required. Sensitive numbers are not required.

JSON Schema for a registered type comes from `export_json_schema`. Any Pydantic model, including `TravelEventSchema`, can use `validation.generate_json_schema`.

## Dates, timezones, and original text

`DateTimeSchema` stores the printed date and time separately from normalized values:

- `original_date` and `original_time` keep the printed text
- `normalized_date` and `normalized_local_time` are set only when the value is unambiguous
- `iana_timezone`, `utc_offset`, and `utc_offset_minutes` describe the zone for that one instant
- `local_datetime` is naive local time
- `utc_datetime` is an aware UTC instant
- `timezone_known` is true only when the zone is known, false when it is explicitly unknown, and null when the document does not say

Do not parse `03/04/2026` into a calendar date inside this library. Leave `normalized_date` empty and keep the original string. Do not invent a check-in time, a night count, or a timezone abbreviation such as `IST`. Departure and arrival each have their own timezone fields. An overnight journey sets `overnight_journey` when that fact is known. It is not inferred from two local clocks in unknown zones.

`original_values` stores printed text for any field whose normalized form is incomplete. `provider_extensions` stores provider-specific scalars only: strings, booleans, numbers, and null. Nested objects are rejected.

Enums are used for status, payment, cabin, transport mode, and the other controlled vocabularies. When the printed word does not map cleanly, leave the enum null and keep the printed word in the matching `*_original` field.

## Evidence

Evidence is attached to the document through `extraction_metadata.evidence`, not copied onto every business object. Each `DocumentEvidenceSchema` requires `field_name` and may include source text, page, location, extraction method, and verification status.

`confidence`, when present, is a number from 0 to 1 supplied by the extractor. It is not a calibrated probability.

## Documents and events

```python
from events import EventType, TravelEventSchema

event = TravelEventSchema(
    event_type=EventType.FLIGHT_DEPARTURE,
    trip_id="trip-200",
    source_document_ids=["doc-flight-1001"],
    traveler_ids=["trv-1"],
    start_datetime={"iana_timezone": "Europe/London", "original_time": "21:30"},
    location={"name": "London Heathrow"},
    destination={"name": "Delhi"},
)
```

One document may be cited by several events. `event_type` is required. Times and places are optional, so a partial derived event can be stored without filling in missing clock times.

## Add a document type

Subclass `BaseDocumentSchema`, or a category base such as `FlightDocumentSchema`, and register the class.

```python
from pydantic import Field
from registry import register_schema
from schemas.base.base_document import BaseDocumentSchema, declare_document_schema

BalloonRideTicketSchema = declare_document_schema(
    "BalloonRideTicketSchema",
    document_type="balloon_ride_ticket",
    base=BaseDocumentSchema,
    description="A ticket for a balloon ride.",
    module=__name__,
    category="activities",
    fields={
        "launch_site": (
            str | None,
            Field(default=None, description="Where the balloon launches."),
        )
    },
)

register_schema(
    "balloon_ride_ticket",
    BalloonRideTicketSchema,
    version="1.0.0",
    description="A ticket for a balloon ride.",
)
```

The registered class must be a `BaseDocumentSchema` subclass, and its declared document type must match the registry key. A new version can be registered beside `1.0.0`. `get_schema(document_type)` returns the highest version. Pass `version=` to select an older one.

A custom check can be added without changing stored values:

```python
from validation import BusinessFinding, register_business_rule, run_business_rules

class NeedsPnr:
    code = "needs_pnr"

    def evaluate(self, model):
        if getattr(model, "DOCUMENT_TYPE", None) == "flight_ticket" and model.pnr is None:
            return [BusinessFinding(code=self.code, message="PNR was not printed.", field_path="pnr")]
        return []

register_business_rule(NeedsPnr(), {"flight_ticket"})
```

Built-in rules report a known timeline that ends before it starts, a stated night count that disagrees with the stay dates, and internal date contradictions. They do not compare local clocks when the timezone is unknown, and they do not fill a missing night count.

## Examples

`examples/` contains one payload for each major category: flight ticket, hotel booking, train ticket, bus ticket, car rental, travel itinerary, passport, travel insurance, cruise booking, tour booking, airport transfer, travel invoice, corporate authorization, and child travel consent. The passport example leaves the document number empty. The flight example has two passengers, two segments, and two different timezones.

## Supported document types

Ninety-eight document types are registered at version `1.0.0`.

### Flight

`flight_ticket`, `flight_booking_confirmation`, `flight_boarding_pass`, `flight_itinerary`, `flight_cancellation`, `flight_reschedule`, `flight_upgrade_confirmation`, `flight_invoice`, `baggage_confirmation`

### Hotel and accommodation

`hotel_booking`, `hotel_confirmation`, `hotel_voucher`, `hotel_invoice`, `hotel_cancellation`, `hotel_reschedule`, `resort_booking`, `hostel_booking`, `vacation_rental`, `homestay_booking`

### Train

`train_ticket`, `train_booking_confirmation`, `railway_reservation`, `rail_pass`, `train_cancellation`, `train_reschedule`

### Bus

`bus_ticket`, `bus_booking_confirmation`, `bus_pass`, `bus_cancellation`, `bus_reschedule`

### Car rental and road transport

`car_rental`, `car_rental_confirmation`, `car_rental_agreement`, `taxi_booking`, `chauffeur_booking`, `vehicle_permit`, `parking_reservation`

### Itinerary

`travel_itinerary`, `multi_city_itinerary`, `trip_plan`, `day_wise_itinerary`, `business_travel_itinerary`, `group_travel_itinerary`, `tour_itinerary`

### Identity and immigration

`passport`, `visa`, `evisa`, `residence_permit`, `travel_authorization`, `entry_permit`, `exit_permit`, `international_driving_permit`

### Insurance and medical

`travel_insurance`, `insurance_certificate`, `insurance_claim`, `medical_travel_certificate`, `vaccination_certificate`, `medical_assistance`

### Cruise and ferry

`cruise_booking`, `cruise_ticket`, `cruise_itinerary`, `ferry_ticket`, `ship_boarding_pass`, `shore_excursion`

### Activities

`tour_booking`, `activity_booking`, `attraction_ticket`, `museum_ticket`, `theme_park_ticket`, `event_ticket`, `safari_booking`, `trekking_permit`, `camping_reservation`, `excursion_voucher`

### Airport and transfers

`airport_transfer`, `airport_pickup`, `airport_dropoff`, `shuttle_booking`, `airport_lounge_pass`, `meet_and_greet`

### Financial

`travel_invoice`, `travel_payment_receipt`, `refund_confirmation`, `booking_transaction`, `travel_expense`, `currency_exchange_receipt`

### Corporate

`corporate_travel_authorization`, `business_trip_approval`, `business_invitation`, `conference_registration`, `exhibition_pass`, `travel_reimbursement`

### Special

`child_travel_consent`, `pet_travel_certificate`, `pet_travel_booking`, `special_assistance`, `wheelchair_assistance`, `travel_emergency_contact`

Event types live on `events.EventType` and include `flight_departure`, `flight_arrival`, `train_departure`, `train_arrival`, `bus_departure`, `bus_arrival`, `hotel_checkin`, `hotel_checkout`, `car_pickup`, `car_return`, `tour_start`, `cruise_departure`, and `visa_expiry`.

## Layout

```text
docs/             classifier explanation
api/              document type endpoint
schemas/          document and shared models
  base/           universal document, enums, validators
  common/         reusable entities
  flight/ ...     one package per document category
  catalog.py      built-in schema list
events/           travel events, separate from documents
registry/         registration, versions, field metadata, JSON Schema export
validation/       validation, partial preservation, business rules
examples/         one example payload per major category
tests/            schema, registry, and serialization tests
```
