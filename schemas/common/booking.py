"""Booking references shared by confirmations, tickets, and reservations."""

from __future__ import annotations

from schemas.base.base_models import F, SchemaModel
from schemas.base.enums import BookingStatus
from schemas.common.datetime import DateTimeSchema
from schemas.common.provider import ProviderSchema


class BookingSchema(SchemaModel):
    """A reservation reference. A booking is not itself a ticket or boarding pass."""

    booking_reference: str | None = F("Booking reference or record locator as printed.")
    confirmation_number: str | None = F("Confirmation number when the document uses one.")
    vendor_reference: str | None = F("Secondary provider reference.")
    booking_status: BookingStatus | None = F("Standardized booking status. Leave null when the wording is unmapped.")
    original_status: str | None = F("Status wording exactly as printed.")
    booked_at: DateTimeSchema | None = F("When the booking was made, when the document says so.")
    provider: ProviderSchema | None = F("Provider that holds the booking.")
    channel: str | None = F("Sales channel as printed, such as website, agency, or counter.")
    agent_name: str | None = F("Agent or seller name as printed.")
