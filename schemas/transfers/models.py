"""Airport transfers, shuttles, lounge access, and meet-and-greet documents."""

from __future__ import annotations

from pydantic import Field

from schemas.base.base_document import BaseDocumentSchema, declare_document_schema
from schemas.base.base_models import F
from schemas.base.enums import BookingStatus
from schemas.common.booking import BookingSchema
from schemas.common.datetime import DateTimeSchema
from schemas.common.location import AirportSchema, LocationSchema
from schemas.common.passenger import PassengerSchema
from schemas.common.payment import PaymentSchema
from schemas.common.person import PersonSchema
from schemas.common.provider import ProviderSchema
from schemas.common.transport import VehicleSchema


class TransferServiceDocumentSchema(BaseDocumentSchema):
    """A ride that picks travelers up and drops them off."""

    provider: ProviderSchema | None = F("Transfer provider.")
    pickup_location: LocationSchema | None = F("Pickup place.")
    dropoff_location: LocationSchema | None = F("Drop-off place.")
    pickup: DateTimeSchema | None = F("Pickup date and time.")
    dropoff: DateTimeSchema | None = F("Expected or actual drop-off time when stated.")
    passengers: list[PassengerSchema] | None = F("Passengers.")
    vehicle: VehicleSchema | None = F("Vehicle when it is described.")
    driver: PersonSchema | None = F("Driver when named.")
    booking: BookingSchema | None = F("Booking reference.")
    booking_status: BookingStatus | None = F("Booking status.")
    payment: PaymentSchema | None = F("Payment information.")
    flight_number: str | None = F("Related flight number as printed.")
    terminal: str | None = F("Terminal as printed.")
    instructions: str | None = F("Pickup or meeting instructions.")
    remarks: str | None = F("Other transfer remarks.")


class LoungePassDocumentSchema(BaseDocumentSchema):
    """Access to an airport lounge. This is not a transfer booking."""

    lounge_name: str | None = F("Lounge name.")
    airport: AirportSchema | None = F("Airport where the lounge is located.")
    terminal: str | None = F("Terminal as printed.")
    holder: PersonSchema | None = F("Person the pass is issued to.")
    guests: list[PersonSchema] | None = F("Additional guests allowed by the pass.")
    valid_from: DateTimeSchema | None = F("When access starts.")
    valid_until: DateTimeSchema | None = F("When access ends.")
    guest_count: int | None = Field(default=None, ge=0, description="Guest count when the pass states one.")
    access_instructions: str | None = F("How to enter the lounge.")
    remarks: str | None = F("Lounge pass remarks.")


_MODULE = __name__


def _transfer(name: str, document_type: str, description: str, **fields: tuple):
    return declare_document_schema(
        name,
        document_type=document_type,
        base=TransferServiceDocumentSchema,
        description=description,
        module=_MODULE,
        category="transfers",
        fields=fields or None,
    )


AirportTransferSchema = _transfer(
    "AirportTransferSchema",
    "airport_transfer",
    "An airport transfer that may be an arrival pickup, a departure drop-off, or a round trip.",
    transfer_direction=(str | None, F("Direction as printed, such as arrival or departure.")),
)

AirportPickupSchema = _transfer(
    "AirportPickupSchema",
    "airport_pickup",
    "A pickup on arrival at an airport.",
    arrival_flight_number=(str | None, F("Arriving flight number the driver is meeting.")),
)

AirportDropoffSchema = _transfer(
    "AirportDropoffSchema",
    "airport_dropoff",
    "A drop-off for a departing flight.",
    departure_flight_number=(str | None, F("Departing flight number.")),
)

ShuttleBookingSchema = _transfer(
    "ShuttleBookingSchema",
    "shuttle_booking",
    "A shared or scheduled shuttle booking.",
    route_name=(str | None, F("Shuttle route name.")),
    stops=(list[LocationSchema] | None, F("Stops the shuttle makes.")),
)

MeetAndGreetSchema = _transfer(
    "MeetAndGreetSchema",
    "meet_and_greet",
    "A meet-and-greet service at an airport or station.",
    greeter_name=(str | None, F("Greeter name when printed.")),
    meeting_point=(LocationSchema | None, F("Where the greeter will wait.")),
    sign_name=(str | None, F("Name that will be written on the greeting sign.")),
)

AirportLoungePassSchema = declare_document_schema(
    "AirportLoungePassSchema",
    document_type="airport_lounge_pass",
    base=LoungePassDocumentSchema,
    description="A pass for an airport lounge. It does not describe a pickup or drop-off.",
    module=_MODULE,
    category="transfers",
)

TRANSFER_SCHEMAS = (
    AirportTransferSchema,
    AirportPickupSchema,
    AirportDropoffSchema,
    ShuttleBookingSchema,
    AirportLoungePassSchema,
    MeetAndGreetSchema,
)
