"""Flight documents.

A booking confirmation records a reservation. A ticket records that the
reservation was ticketed. A boarding pass is the airport document for a
specific segment. Those roles stay on separate schemas even when some fields
overlap.
"""

from __future__ import annotations

from pydantic import Field

from schemas.base.base_document import BaseDocumentSchema, declare_document_schema
from schemas.base.base_models import F, SchemaModel
from schemas.base.enums import BookingStatus, CabinClass
from schemas.common.baggage import BaggageAllowanceSchema, BaggageItemSchema
from schemas.common.booking import BookingSchema
from schemas.common.cancellation import CancellationPolicySchema
from schemas.common.datetime import DateTimeSchema
from schemas.common.location import AirportSchema
from schemas.common.passenger import PassengerSchema
from schemas.common.payment import CurrencySchema, LineItemSchema, PaymentSchema
from schemas.common.provider import ProviderSchema
from schemas.common.transport import SeatAssignmentSchema


class FlightSegmentSchema(SchemaModel):
    """One flight leg. Departure and arrival each have their own time and timezone."""

    segment_id: str | None = F("Identifier for this segment within the document.")
    airline: ProviderSchema | None = F("Marketing airline for this segment.")
    operating_airline: ProviderSchema | None = F("Operating airline when it differs from the marketing airline.")
    flight_number: str | None = F("Flight number as printed, including the airline prefix when shown.")
    departure_airport: AirportSchema | None = F("Airport where this segment departs.")
    arrival_airport: AirportSchema | None = F("Airport where this segment arrives.")
    departure: DateTimeSchema | None = F("Departure date, local time, and timezone. The timezone may be unknown.")
    arrival: DateTimeSchema | None = F("Arrival date, local time, and timezone. It is independent of departure.")
    departure_terminal: str | None = F("Departure terminal as printed.")
    arrival_terminal: str | None = F("Arrival terminal as printed.")
    departure_gate: str | None = F("Departure gate as printed.")
    arrival_gate: str | None = F("Arrival gate as printed.")
    cabin_class: CabinClass | None = F("Cabin class when it maps to the standard list.")
    booking_class: str | None = F("Fare or booking class code exactly as printed.")
    aircraft_type: str | None = F("Aircraft type as printed.")
    seat: str | None = F("Seat printed for this segment when there is a single seat.")
    baggage_allowance: BaggageAllowanceSchema | None = F("Baggage allowance for this segment.")
    segment_status: BookingStatus | None = F("Status of this segment.")
    overnight_journey: bool | None = F("True when this segment is an overnight journey.")
    international: bool | None = F("True or false only when the segment's countries establish it.")
    duration_original: str | None = F("Duration exactly as printed.")
    duration_minutes: int | None = Field(
        default=None,
        ge=0,
        description="Duration in minutes only when the document states a duration that is known in minutes.",
    )
    distance_original: str | None = F("Distance exactly as printed, including the unit.")


class FlightCouponSchema(SchemaModel):
    """One coupon of an issued ticket."""

    coupon_number: str | None = F("Coupon number as printed.")
    segment_ref: str | None = F("Segment this coupon applies to.")
    ticket_number: str | None = F("Ticket number this coupon belongs to.")
    status: str | None = F("Coupon status as printed.")
    fare_basis: str | None = F("Fare basis code as printed.")
    baggage_allowance: BaggageAllowanceSchema | None = F("Baggage allowance printed on the coupon.")
    original_text: str | None = F("Coupon line exactly as printed.")


class FareSchema(SchemaModel):
    """Fare details from a ticket or invoice. Unparsed fare text is preserved."""

    fare_basis: str | None = F("Fare basis as printed.")
    fare_family: str | None = F("Fare family or brand as printed.")
    base_fare: CurrencySchema | None = F("Base fare when an amount is shown.")
    taxes: CurrencySchema | None = F("Tax total when an amount is shown.")
    total: CurrencySchema | None = F("Total fare when an amount is shown.")
    fare_construction: str | None = F("Fare construction line exactly as printed.")
    original_text: str | None = F("Fare block exactly as printed.")


class FlightDocumentSchema(BaseDocumentSchema):
    """Fields shared by flight tickets, confirmations, passes, and related documents."""

    airline: ProviderSchema | None = F("Airline that issued or markets the document.")
    operating_carriers: list[ProviderSchema] | None = F("Operating carriers named on the document.")
    pnr: str | None = F("Passenger name record or record locator as printed.")
    booking: BookingSchema | None = F("Booking reference. Present on a confirmation and often also on a ticket.")
    booking_status: BookingStatus | None = F("Status of the flight booking.")
    passengers: list[PassengerSchema] | None = F("Passengers named on the document.")
    segments: list[FlightSegmentSchema] | None = F("Flight segments in journey order.")
    seat_assignments: list[SeatAssignmentSchema] | None = F("Seats linked to passengers and segments.")
    baggage_allowance: BaggageAllowanceSchema | None = F("Document-level baggage allowance when one is printed.")
    payment: PaymentSchema | None = F("Payment information printed on the document.")
    remarks: str | None = F("Remarks or endorsements that do not fit a specific field.")


_CATEGORY = "flight"
_MODULE = __name__


def _flight(name: str, document_type: str, description: str, **fields: tuple) -> type[FlightDocumentSchema]:
    return declare_document_schema(
        name,
        document_type=document_type,
        base=FlightDocumentSchema,
        description=description,
        module=_MODULE,
        category=_CATEGORY,
        fields=fields or None,
    )


FlightTicketSchema = _flight(
    "FlightTicketSchema",
    "flight_ticket",
    "An issued flight ticket or e-ticket. Ticket numbers and coupons distinguish it from a booking confirmation.",
    ticket_numbers=(list[str] | None, F("Ticket numbers printed on the issued ticket.")),
    coupons=(list[FlightCouponSchema] | None, F("Ticket coupons.")),
    endorsements=(str | None, F("Endorsement or restriction text exactly as printed.")),
    fare=(FareSchema | None, F("Fare breakdown for the issued ticket.")),
)

FlightBookingConfirmationSchema = _flight(
    "FlightBookingConfirmationSchema",
    "flight_booking_confirmation",
    "A flight reservation confirmation. It confirms a booking and is not an issued ticket or a boarding pass.",
    ticketing_deadline=(DateTimeSchema | None, F("Deadline to issue tickets, when the confirmation states one.")),
    hold_expiry=(DateTimeSchema | None, F("When a held reservation expires, when the confirmation states it.")),
)

FlightBoardingPassSchema = _flight(
    "FlightBoardingPassSchema",
    "flight_boarding_pass",
    "A boarding pass for airport acceptance of one or more flight segments. It is not a booking confirmation.",
    boarding_time=(DateTimeSchema | None, F("Boarding time. Leave the clock time empty when it was not printed.")),
    boarding_group=(str | None, F("Boarding group as printed.")),
    sequence_number=(str | None, F("Boarding sequence number as printed.")),
    bar_code_reference=(str | None, F("Barcode or QR reference when the document exposes one as text.")),
    fast_track=(bool | None, F("True when the pass grants a fast-track or priority boarding marker.")),
)

FlightItinerarySchema = _flight(
    "FlightItinerarySchema",
    "flight_itinerary",
    "A flight itinerary listing one or more segments. It may accompany a booking before a ticket is issued.",
    itinerary_name=(str | None, F("Name printed on the itinerary.")),
)

FlightCancellationSchema = _flight(
    "FlightCancellationSchema",
    "flight_cancellation",
    "A notice that a flight booking or ticket was cancelled.",
    cancelled_at=(DateTimeSchema | None, F("When the cancellation was recorded, when the notice says so.")),
    cancellation_reason=(str | None, F("Cancellation reason as printed.")),
    cancellation_policy=(CancellationPolicySchema | None, F("Cancellation terms printed on the notice.")),
    refund=(PaymentSchema | None, F("Refund described by the cancellation notice.")),
    cancelled_segment_refs=(list[str] | None, F("Segments named as cancelled.")),
)

FlightRescheduleSchema = _flight(
    "FlightRescheduleSchema",
    "flight_reschedule",
    "A notice of a flight change. Previous and revised segments are stored separately.",
    previous_segments=(list[FlightSegmentSchema] | None, F("Segments before the change.")),
    revised_segments=(list[FlightSegmentSchema] | None, F("Segments after the change.")),
    changed_at=(DateTimeSchema | None, F("When the change was recorded.")),
    change_fee=(CurrencySchema | None, F("Change fee when an amount is stated.")),
)

FlightUpgradeConfirmationSchema = _flight(
    "FlightUpgradeConfirmationSchema",
    "flight_upgrade_confirmation",
    "Confirmation that a passenger moved from one cabin to another.",
    original_cabin_class=(CabinClass | None, F("Cabin before the upgrade.")),
    upgraded_cabin_class=(CabinClass | None, F("Cabin after the upgrade.")),
    upgrade_status=(str | None, F("Upgrade status as printed.")),
    upgraded_segment_refs=(list[str] | None, F("Segments covered by the upgrade.")),
)

FlightInvoiceSchema = _flight(
    "FlightInvoiceSchema",
    "flight_invoice",
    "An invoice for flight charges. It records money owed or paid and is not a boarding pass.",
    invoice_number=(str | None, F("Invoice number as printed.")),
    line_items=(list[LineItemSchema] | None, F("Invoice lines.")),
    amount_due=(CurrencySchema | None, F("Amount due when the invoice states one.")),
    fare=(FareSchema | None, F("Fare breakdown when the invoice includes one.")),
)

BaggageConfirmationSchema = _flight(
    "BaggageConfirmationSchema",
    "baggage_confirmation",
    "A confirmation of checked or prepaid baggage.",
    baggage_items=(list[BaggageItemSchema] | None, F("Bags named on the confirmation.")),
    claim_reference=(str | None, F("Baggage claim or prepaid baggage reference.")),
)

FLIGHT_SCHEMAS = (
    FlightTicketSchema,
    FlightBookingConfirmationSchema,
    FlightBoardingPassSchema,
    FlightItinerarySchema,
    FlightCancellationSchema,
    FlightRescheduleSchema,
    FlightUpgradeConfirmationSchema,
    FlightInvoiceSchema,
    BaggageConfirmationSchema,
)
