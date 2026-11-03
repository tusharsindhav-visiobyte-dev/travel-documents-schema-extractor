"""Accommodation properties and guests."""

from __future__ import annotations

from pydantic import Field

from schemas.base.base_models import F, SchemaModel
from schemas.base.enums import PropertyType
from schemas.common.contact import ContactSchema
from schemas.common.datetime import TimezoneSchema
from schemas.common.location import AddressSchema
from schemas.common.traveler import TravelerSchema


class AccommodationSchema(SchemaModel):
    """A property where a traveler stays. Star ratings keep the printed form."""

    property_id: str | None = F("Application or provider identifier for the property.")
    name: str | None = F("Property name.")
    property_type: PropertyType | None = F("Standardized property type. Leave null when it is unclear.")
    property_type_original: str | None = F("Property type exactly as printed.")
    chain_name: str | None = F("Hotel or resort chain when it is named.")
    star_rating: str | None = F("Star rating exactly as printed, such as 4-star or 4.5.")
    star_rating_value: float | None = Field(
        default=None,
        ge=0,
        description="Numeric star rating only when the document states a number.",
    )
    address: AddressSchema | None = F("Property address.")
    contact: ContactSchema | None = F("Property contact details.")
    timezone: TimezoneSchema | None = F("Timezone of the property. Check-in and check-out still carry their own times.")
    original_name: str | None = F("Property name exactly as printed.")


class GuestSchema(TravelerSchema):
    """A guest named on an accommodation document."""

    guest_type: str | None = F("Guest type as printed, such as adult or child.")
    loyalty_number: str | None = F("Property loyalty number as printed.")
    room_assignment: str | None = F("Room or bed assigned to this guest, when printed.")
    is_primary_guest: bool | None = F("True when the document marks this guest as the lead guest.")
