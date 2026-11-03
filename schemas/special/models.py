"""Consent, pet travel, assistance, and emergency-contact documents."""

from __future__ import annotations

from decimal import Decimal

from pydantic import Field

from schemas.base.base_document import BaseDocumentSchema, declare_document_schema
from schemas.base.base_models import F, SchemaModel
from schemas.common.contact import EmergencyContactSchema
from schemas.common.datetime import DateTimeSchema
from schemas.common.location import LocationSchema
from schemas.common.person import PersonSchema
from schemas.common.provider import ProviderSchema


class PetSchema(SchemaModel):
    """An animal traveling with a person. Identifiers stay optional."""

    name: str | None = F("Pet name.")
    species: str | None = F("Species as printed.")
    breed: str | None = F("Breed as printed.")
    microchip_id: str | None = F("Microchip identifier when printed.")
    weight_kg: Decimal | None = Field(
        default=None,
        ge=0,
        description="Weight in kilograms only when the unit is kilograms.",
    )
    weight_original: str | None = F("Weight exactly as printed.")
    color: str | None = F("Color as printed.")
    date_of_birth: DateTimeSchema | None = F("Date of birth when shown.")


class SpecialDocumentSchema(BaseDocumentSchema):
    """A travel document for consent, animals, assistance, or emergency contacts."""

    valid_from: DateTimeSchema | None = F("When the document becomes valid.")
    valid_until: DateTimeSchema | None = F("When the document stops being valid.")
    remarks: str | None = F("Remarks.")


_MODULE = __name__


def _special(name: str, document_type: str, description: str, **fields: tuple):
    return declare_document_schema(
        name,
        document_type=document_type,
        base=SpecialDocumentSchema,
        description=description,
        module=_MODULE,
        category="special",
        fields=fields or None,
    )


ChildTravelConsentSchema = _special(
    "ChildTravelConsentSchema",
    "child_travel_consent",
    "Consent for a child to travel. Identity numbers of the child or guardians are optional.",
    child=(PersonSchema | None, F("Child the consent covers.")),
    guardians=(list[PersonSchema] | None, F("Parents or guardians who give consent.")),
    accompanying_adult=(PersonSchema | None, F("Adult accompanying the child.")),
    consent_statement=(str | None, F("Consent wording exactly as printed.")),
    destinations=(list[LocationSchema] | None, F("Destinations covered by the consent.")),
)

PetTravelCertificateSchema = _special(
    "PetTravelCertificateSchema",
    "pet_travel_certificate",
    "A health or travel certificate for a pet.",
    pet=(PetSchema | None, F("Animal the certificate covers.")),
    owner=(PersonSchema | None, F("Owner named on the certificate.")),
    veterinarian_name=(str | None, F("Veterinarian name as printed.")),
    health_notes=(str | None, F("Health notes exactly as printed.")),
)

PetTravelBookingSchema = _special(
    "PetTravelBookingSchema",
    "pet_travel_booking",
    "A booking to transport a pet.",
    pet=(PetSchema | None, F("Animal being transported.")),
    owner=(PersonSchema | None, F("Owner who made the booking.")),
    carrier=(ProviderSchema | None, F("Carrier transporting the pet.")),
    kennel_type=(str | None, F("Kennel or cabin arrangement as printed.")),
)

SpecialAssistanceSchema = _special(
    "SpecialAssistanceSchema",
    "special_assistance",
    "A request or confirmation of special assistance while traveling.",
    traveler=(PersonSchema | None, F("Traveler who needs assistance.")),
    assistance_types=(list[str] | None, F("Assistance types as printed.")),
    provider=(ProviderSchema | None, F("Provider arranging the assistance.")),
    notes=(str | None, F("Assistance notes as printed.")),
)

WheelchairAssistanceSchema = _special(
    "WheelchairAssistanceSchema",
    "wheelchair_assistance",
    "Wheelchair assistance arranged for a traveler.",
    traveler=(PersonSchema | None, F("Traveler receiving assistance.")),
    wheelchair_type=(str | None, F("Wheelchair type as printed.")),
    own_wheelchair=(bool | None, F("True when the document says the traveler uses their own wheelchair.")),
    assistance_points=(list[str] | None, F("Airports or stations where assistance is arranged.")),
    battery_note=(str | None, F("Battery note exactly as printed.")),
)

TravelEmergencyContactSchema = _special(
    "TravelEmergencyContactSchema",
    "travel_emergency_contact",
    "Emergency contacts recorded for a traveler.",
    traveler=(PersonSchema | None, F("Traveler these contacts belong to.")),
    contacts=(list[EmergencyContactSchema] | None, F("Emergency contacts in the order given.")),
)

SPECIAL_SCHEMAS = (
    ChildTravelConsentSchema,
    PetTravelCertificateSchema,
    PetTravelBookingSchema,
    SpecialAssistanceSchema,
    WheelchairAssistanceSchema,
    TravelEmergencyContactSchema,
)
