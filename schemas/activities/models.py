"""Tours, attractions, events, and outdoor activity documents."""

from __future__ import annotations

from pydantic import Field

from schemas.base.base_document import BaseDocumentSchema, declare_document_schema
from schemas.base.base_models import F
from schemas.base.enums import BookingStatus
from schemas.common.booking import BookingSchema
from schemas.common.contact import ContactSchema
from schemas.common.datetime import DateTimeSchema
from schemas.common.location import LocationSchema
from schemas.common.payment import PaymentSchema
from schemas.common.provider import ProviderSchema
from schemas.common.transport import RouteSchema
from schemas.common.traveler import TravelerSchema


class ActivityDocumentSchema(BaseDocumentSchema):
    """A booked tour, ticket, permit, or reservation for an activity."""

    provider: ProviderSchema | None = F("Operator or seller.")
    title: str | None = F("Activity, attraction, or event title.")
    venue: LocationSchema | None = F("Where the activity takes place.")
    start: DateTimeSchema | None = F("Start date and time. A missing clock time stays missing.")
    end: DateTimeSchema | None = F("End date and time.")
    participants: list[TravelerSchema] | None = F("People covered by the booking or ticket.")
    booking: BookingSchema | None = F("Booking reference.")
    booking_status: BookingStatus | None = F("Booking status.")
    payment: PaymentSchema | None = F("Payment information.")
    ticket_numbers: list[str] | None = F("Ticket numbers when the document lists them.")
    quantity: int | None = Field(default=None, ge=0, description="Ticket or place count when stated.")
    inclusions: list[str] | None = F("Items included.")
    exclusions: list[str] | None = F("Items excluded.")
    remarks: str | None = F("Remarks printed on the activity document.")


_MODULE = __name__


def _activity(name: str, document_type: str, description: str, **fields: tuple):
    return declare_document_schema(
        name,
        document_type=document_type,
        base=ActivityDocumentSchema,
        description=description,
        module=_MODULE,
        category="activities",
        fields=fields or None,
    )


TourBookingSchema = _activity(
    "TourBookingSchema",
    "tour_booking",
    "A booking for a guided or packaged tour.",
    tour_name=(str | None, F("Tour name.")),
    destinations=(list[LocationSchema] | None, F("Destinations the tour visits.")),
    duration_original=(str | None, F("Tour duration exactly as printed.")),
)

ActivityBookingSchema = _activity(
    "ActivityBookingSchema",
    "activity_booking",
    "A booking for an experience or activity that is not a specific attraction ticket.",
    activity_type=(str | None, F("Activity type as printed.")),
)

AttractionTicketSchema = _activity(
    "AttractionTicketSchema",
    "attraction_ticket",
    "A ticket for an attraction.",
    attraction_name=(str | None, F("Attraction name.")),
    validity_start=(DateTimeSchema | None, F("When the ticket becomes valid.")),
    validity_end=(DateTimeSchema | None, F("When the ticket stops being valid.")),
)

MuseumTicketSchema = _activity(
    "MuseumTicketSchema",
    "museum_ticket",
    "A ticket for a museum or a specific exhibition.",
    museum_name=(str | None, F("Museum name.")),
    exhibition_name=(str | None, F("Exhibition name when the ticket is for one exhibition.")),
)

ThemeParkTicketSchema = _activity(
    "ThemeParkTicketSchema",
    "theme_park_ticket",
    "A ticket for a theme park.",
    park_name=(str | None, F("Park name.")),
    access_level=(str | None, F("Access level or ticket tier as printed.")),
)

EventTicketSchema = _activity(
    "EventTicketSchema",
    "event_ticket",
    "A ticket for a show, match, or other event.",
    event_name=(str | None, F("Event name.")),
    section=(str | None, F("Section as printed.")),
    seat=(str | None, F("Seat as printed.")),
    row=(str | None, F("Row as printed.")),
)

SafariBookingSchema = _activity(
    "SafariBookingSchema",
    "safari_booking",
    "A safari booking.",
    park_name=(str | None, F("Park or reserve name.")),
    guide_name=(str | None, F("Guide name when printed.")),
    vehicle_description=(str | None, F("Safari vehicle description as printed.")),
)

TrekkingPermitSchema = _activity(
    "TrekkingPermitSchema",
    "trekking_permit",
    "A permit to trek a stated route during a stated period.",
    permit_number=(str | None, F("Permit number when printed.")),
    route_name=(str | None, F("Route name.")),
    route=(RouteSchema | None, F("Route origin, destination, and stops.")),
    valid_from=(DateTimeSchema | None, F("When the permit becomes valid.")),
    valid_until=(DateTimeSchema | None, F("When the permit stops being valid.")),
    emergency_contact=(ContactSchema | None, F("Emergency contact printed on the permit.")),
    group_size=(int | None, Field(default=None, ge=0, description="Group size when stated.")),
)

CampingReservationSchema = _activity(
    "CampingReservationSchema",
    "camping_reservation",
    "A reservation for a campsite or pitch.",
    campsite_name=(str | None, F("Campsite name.")),
    pitch=(str | None, F("Pitch or site identifier as printed.")),
    check_in=(DateTimeSchema | None, F("Check-in. A missing clock time stays missing.")),
    check_out=(DateTimeSchema | None, F("Check-out. A missing clock time stays missing.")),
    guest_count=(int | None, Field(default=None, ge=0, description="Guest count when stated.")),
)

ExcursionVoucherSchema = _activity(
    "ExcursionVoucherSchema",
    "excursion_voucher",
    "A voucher to redeem an excursion.",
    voucher_number=(str | None, F("Voucher number as printed.")),
    redeem_instructions=(str | None, F("How to redeem the voucher.")),
)

ACTIVITY_SCHEMAS = (
    TourBookingSchema,
    ActivityBookingSchema,
    AttractionTicketSchema,
    MuseumTicketSchema,
    ThemeParkTicketSchema,
    EventTicketSchema,
    SafariBookingSchema,
    TrekkingPermitSchema,
    CampingReservationSchema,
    ExcursionVoucherSchema,
)
