"""Contact details as printed on a travel document."""

from __future__ import annotations

from pydantic import Field

from schemas.base.base_models import F, SchemaModel
from schemas.common.location import AddressSchema


class ContactSchema(SchemaModel):
    """A contact point. Phone numbers and emails are kept as printed."""

    contact_name: str | None = F("Name attached to this contact point.")
    email: str | None = F("Email address as printed. It is not rewritten.")
    phone: str | None = F("Telephone number as printed. It is not rewritten into another format.")
    url: str | None = F("Web or deep-link address as printed.")
    contact_role: str | None = F("Role of this contact, such as front desk or emergency.")
    address: AddressSchema | None = F("Postal address for this contact.")


class EmergencyContactSchema(SchemaModel):
    """A person to contact if a traveler needs help."""

    name: str | None = F("Contact name as printed.")
    relationship: str | None = F("Relationship to the traveler as printed.")
    contact: ContactSchema | None = F("How to reach this person.")
    priority: int | None = Field(
        default=None,
        ge=1,
        description="Contact order when the document ranks contacts.",
    )
    notes: str | None = F("Notes printed beside the contact.")
