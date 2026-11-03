"""Bus documents. A ticket, a booking confirmation, and a pass are separate schemas."""

from __future__ import annotations

from pydantic import Field

from schemas.base.base_document import BaseDocumentSchema, declare_document_schema
from schemas.base.base_models import F, SchemaModel
from schemas.base.enums import BookingStatus
from schemas.common.booking import BookingSchema
from schemas.common.datetime import DateTimeSchema
from schemas.common.location import LocationSchema
from schemas.common.passenger import PassengerSchema
from schemas.common.payment import PaymentSchema
from schemas.common.provider import ProviderSchema
from schemas.common.transport import SeatAssignmentSchema


class BusSegmentSchema(SchemaModel):
    """One bus leg, including boarding and dropping points when they are printed."""

    segment_id: str | None = F("Identifier for this bus segment.")
    departure_location: LocationSchema | None = F("Departure city, station, or stop.")
    arrival_location: LocationSchema | None = F("Arrival city, station, or stop.")
    departure: DateTimeSchema | None = F("Departure date, time, and timezone.")
    arrival: DateTimeSchema | None = F("Arrival date, time, and timezone.")
    boarding_point: LocationSchema | None = F("Boarding point when it is more specific than the departure location.")
    dropping_point: LocationSchema | None = F("Dropping point when it is more specific than the arrival location.")
    seat: str | None = F("Seat number as printed.")
    platform: str | None = F("Platform or bay when it is printed.")
    overnight_journey: bool | None = F("True when the segment is an overnight journey.")
    international: bool | None = F("True or false only when the segment's countries establish it.")


class BusDocumentSchema(BaseDocumentSchema):
    """Fields shared by bus tickets, confirmations, passes, and related notices."""

    operator: ProviderSchema | None = F("Bus operator.")
    bus_number: str | None = F("Bus or service number as printed.")
    bus_type: str | None = F("Short bus type label when it is already a simple name.")
    bus_type_original: str | None = F("Bus type exactly as printed, such as seater or sleeper.")
    segments: list[BusSegmentSchema] | None = F("Bus segments in journey order.")
    passengers: list[PassengerSchema] | None = F("Passengers named on the document.")
    seat_assignments: list[SeatAssignmentSchema] | None = F("Seat assignments.")
    booking: BookingSchema | None = F("Booking reference.")
    booking_status: BookingStatus | None = F("Booking status.")
    payment: PaymentSchema | None = F("Payment information.")
    remarks: str | None = F("Remarks printed on the bus document.")


_CATEGORY = "bus"
_MODULE = __name__


def _bus(name: str, document_type: str, description: str, **fields: tuple) -> type[BusDocumentSchema]:
    return declare_document_schema(
        name,
        document_type=document_type,
        base=BusDocumentSchema,
        description=description,
        module=_MODULE,
        category=_CATEGORY,
        fields=fields or None,
    )


BusTicketSchema = _bus(
    "BusTicketSchema",
    "bus_ticket",
    "An issued bus ticket.",
    ticket_number=(str | None, F("Ticket number as printed.")),
)

BusBookingConfirmationSchema = _bus(
    "BusBookingConfirmationSchema",
    "bus_booking_confirmation",
    "A confirmation that a bus booking exists. It is not itself the ticket.",
    confirmation_number=(str | None, F("Confirmation number as printed.")),
)

BusPassSchema = _bus(
    "BusPassSchema",
    "bus_pass",
    "A bus pass valid for a period or a set of routes.",
    pass_name=(str | None, F("Pass product name.")),
    validity_start=(DateTimeSchema | None, F("When the pass becomes valid.")),
    validity_end=(DateTimeSchema | None, F("When the pass stops being valid.")),
    covered_routes=(list[str] | None, F("Routes the pass covers, as printed.")),
)

BusCancellationSchema = _bus(
    "BusCancellationSchema",
    "bus_cancellation",
    "A notice that a bus ticket or booking was cancelled.",
    cancelled_at=(DateTimeSchema | None, F("When the cancellation was recorded.")),
    cancellation_reason=(str | None, F("Cancellation reason as printed.")),
    refund=(PaymentSchema | None, F("Refund described by the notice.")),
)

BusRescheduleSchema = _bus(
    "BusRescheduleSchema",
    "bus_reschedule",
    "A notice that a bus journey changed.",
    previous_segments=(list[BusSegmentSchema] | None, F("Segments before the change.")),
    revised_segments=(list[BusSegmentSchema] | None, F("Segments after the change.")),
    changed_at=(DateTimeSchema | None, F("When the change was recorded.")),
)

BUS_SCHEMAS = (
    BusTicketSchema,
    BusBookingConfirmationSchema,
    BusPassSchema,
    BusCancellationSchema,
    BusRescheduleSchema,
)
