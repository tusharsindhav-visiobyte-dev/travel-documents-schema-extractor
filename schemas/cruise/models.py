"""Cruise, ferry, and ship documents."""

from __future__ import annotations

from schemas.base.base_document import BaseDocumentSchema, declare_document_schema
from schemas.base.base_models import F, SchemaModel
from schemas.base.enums import BookingStatus
from schemas.common.booking import BookingSchema
from schemas.common.datetime import DateTimeSchema
from schemas.common.location import LocationSchema
from schemas.common.passenger import PassengerSchema
from schemas.common.payment import CurrencySchema, PaymentSchema
from schemas.common.provider import ProviderSchema
from schemas.common.transport import VehicleSchema


class PortCallSchema(SchemaModel):
    """A scheduled stop at a port."""

    port: LocationSchema | None = F("Port.")
    arrival: DateTimeSchema | None = F("Arrival at the port.")
    departure: DateTimeSchema | None = F("Departure from the port.")
    overnight: bool | None = F("True when the ship stays overnight.")
    notes: str | None = F("Port-call notes as printed.")


class VesselDocumentSchema(BaseDocumentSchema):
    """A journey on a ship, ferry, or cruise vessel."""

    operator: ProviderSchema | None = F("Cruise line, ferry operator, or ship owner.")
    vessel_name: str | None = F("Ship or ferry name.")
    vessel_type: str | None = F("Vessel type as printed.")
    passengers: list[PassengerSchema] | None = F("Passengers.")
    departure_port: LocationSchema | None = F("Port of departure.")
    arrival_port: LocationSchema | None = F("Port of arrival.")
    departure: DateTimeSchema | None = F("Departure date, time, and timezone.")
    arrival: DateTimeSchema | None = F("Arrival date, time, and timezone.")
    cabin_number: str | None = F("Cabin number as printed.")
    cabin_category: str | None = F("Cabin category as printed.")
    ports_of_call: list[PortCallSchema] | None = F("Intermediate ports in order.")
    booking: BookingSchema | None = F("Booking reference.")
    booking_status: BookingStatus | None = F("Booking status.")
    payment: PaymentSchema | None = F("Payment information.")
    overnight_journey: bool | None = F("True when the sailing is overnight.")
    international: bool | None = F("True or false only when the route's countries establish it.")
    remarks: str | None = F("Remarks printed on the vessel document.")


_MODULE = __name__


def _vessel(name: str, document_type: str, description: str, **fields: tuple):
    return declare_document_schema(
        name,
        document_type=document_type,
        base=VesselDocumentSchema,
        description=description,
        module=_MODULE,
        category="cruise",
        fields=fields or None,
    )


CruiseBookingSchema = _vessel(
    "CruiseBookingSchema",
    "cruise_booking",
    "A cruise booking. It is not the cruise ticket or the boarding pass.",
    deposit=(CurrencySchema | None, F("Deposit amount when stated.")),
    balance_due=(CurrencySchema | None, F("Remaining balance when stated.")),
    dining_seating=(str | None, F("Dining seating as printed.")),
)

CruiseTicketSchema = _vessel(
    "CruiseTicketSchema",
    "cruise_ticket",
    "An issued cruise ticket.",
    ticket_number=(str | None, F("Ticket number as printed.")),
)

CruiseItinerarySchema = _vessel(
    "CruiseItinerarySchema",
    "cruise_itinerary",
    "A cruise itinerary listing ports and dates.",
    itinerary_name=(str | None, F("Itinerary name.")),
    sea_days=(list[str] | None, F("Sea days as labeled on the itinerary.")),
)

FerryTicketSchema = _vessel(
    "FerryTicketSchema",
    "ferry_ticket",
    "A ferry ticket, including a vehicle when one is carried.",
    ticket_number=(str | None, F("Ticket number as printed.")),
    vehicle=(VehicleSchema | None, F("Vehicle traveling on the ferry.")),
    boarding_point=(LocationSchema | None, F("Boarding point when it is more specific than the departure port.")),
)

ShipBoardingPassSchema = _vessel(
    "ShipBoardingPassSchema",
    "ship_boarding_pass",
    "A boarding pass for a ship. It is the embarkation document, not the booking confirmation.",
    boarding_time=(DateTimeSchema | None, F("Boarding time. Leave the clock time empty when it was not printed.")),
    terminal=(str | None, F("Terminal as printed.")),
    sequence_number=(str | None, F("Boarding sequence as printed.")),
    bar_code_reference=(str | None, F("Barcode reference when exposed as text.")),
)

ShoreExcursionSchema = _vessel(
    "ShoreExcursionSchema",
    "shore_excursion",
    "A shore excursion sold or vouchered with a cruise.",
    excursion_name=(str | None, F("Excursion name.")),
    meeting_point=(LocationSchema | None, F("Where guests meet for the excursion.")),
    start=(DateTimeSchema | None, F("Excursion start.")),
    end=(DateTimeSchema | None, F("Excursion end.")),
    inclusions=(list[str] | None, F("Items included in the excursion.")),
)

CRUISE_SCHEMAS = (
    CruiseBookingSchema,
    CruiseTicketSchema,
    CruiseItinerarySchema,
    FerryTicketSchema,
    ShipBoardingPassSchema,
    ShoreExcursionSchema,
)
