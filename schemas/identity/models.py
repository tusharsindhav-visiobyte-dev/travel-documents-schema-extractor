"""Identity and immigration documents.

Document numbers, nationality, and dates are optional. A partial passport or
visa record is valid when those values were not on the source or are withheld.
"""

from __future__ import annotations

from pydantic import Field, field_validator

from schemas.base.base_document import BaseDocumentSchema, declare_document_schema
from schemas.base.base_models import F
from schemas.base.enums import EntryPermission
from schemas.base.validators import validate_country_code
from schemas.common.datetime import DateTimeSchema
from schemas.common.person import PersonSchema
from schemas.common.provider import OrganizationSchema


class IdentityDocumentSchema(BaseDocumentSchema):
    """Shared fields for passports, visas, permits, and travel authorizations."""

    identity_document_number: str | None = F(
        "Document number when it is available. Leave null when it is missing or withheld."
    )
    issuing_country: str | None = F("Issuing country name as printed.")
    issuing_country_code: str | None = F("Issuing country code when it is known.")
    nationality: str | None = F("Nationality as printed. Leave null when the document does not state it.")
    holder: PersonSchema | None = F("Person the document belongs to.")
    expiry_date: DateTimeSchema | None = F("Expiry date when it is shown.")
    validity_start: DateTimeSchema | None = F("Start of the validity period.")
    validity_end: DateTimeSchema | None = F("End of the validity period.")
    entries: EntryPermission | None = F("Standardized entry permission. Leave null when the wording is unmapped.")
    entries_original: str | None = F("Entry permission exactly as printed, such as single or multiple.")
    permitted_stay: str | None = F("Permitted stay exactly as printed.")
    permitted_stay_days: int | None = Field(
        default=None,
        ge=0,
        description="Permitted stay in days only when the document states a number of days.",
    )
    place_of_issue: str | None = F("Place of issue as printed.")
    remarks: str | None = F("Remarks or observations printed on the document.")

    @field_validator("issuing_country_code")
    @classmethod
    def _issuing_country_code(cls, value: str | None) -> str | None:
        return validate_country_code(value)


_MODULE = __name__


def _identity(name: str, document_type: str, description: str, **fields: tuple):
    return declare_document_schema(
        name,
        document_type=document_type,
        base=IdentityDocumentSchema,
        description=description,
        module=_MODULE,
        category="identity",
        fields=fields or None,
    )


PassportSchema = _identity(
    "PassportSchema",
    "passport",
    "A passport. The passport number is optional because it may be unavailable.",
    passport_type=(str | None, F("Passport type code or label as printed.")),
    issuing_authority=(OrganizationSchema | None, F("Authority that issued the passport.")),
)

VisaSchema = _identity(
    "VisaSchema",
    "visa",
    "A visa placed in a passport or issued as a separate document.",
    visa_type=(str | None, F("Visa type as printed.")),
    visa_category=(str | None, F("Visa category as printed.")),
    linked_passport_number=(str | None, F("Passport number the visa refers to, when printed and available.")),
)

EVisaSchema = _identity(
    "EVisaSchema",
    "evisa",
    "An electronic visa. Application and authorization numbers are optional.",
    application_number=(str | None, F("Electronic visa application number.")),
    authorization_number=(str | None, F("Electronic authorization number.")),
)

ResidencePermitSchema = _identity(
    "ResidencePermitSchema",
    "residence_permit",
    "A residence permit used for travel or stay.",
    permit_type=(str | None, F("Permit type as printed.")),
    residence_country=(str | None, F("Country of residence named on the permit.")),
)

TravelAuthorizationSchema = _identity(
    "TravelAuthorizationSchema",
    "travel_authorization",
    "An electronic travel authorization such as a program approval. The program name is preserved as printed.",
    authorization_program=(str | None, F("Authorization program name as printed.")),
    application_number=(str | None, F("Application number when it is printed.")),
)

EntryPermitSchema = _identity(
    "EntryPermitSchema",
    "entry_permit",
    "Permission to enter a country or territory.",
    port_of_entry=(str | None, F("Port of entry as printed.")),
)

ExitPermitSchema = _identity(
    "ExitPermitSchema",
    "exit_permit",
    "Permission to leave a country or territory.",
    port_of_exit=(str | None, F("Port of exit as printed.")),
)

InternationalDrivingPermitSchema = _identity(
    "InternationalDrivingPermitSchema",
    "international_driving_permit",
    "An international driving permit. Vehicle categories are optional.",
    vehicle_categories=(list[str] | None, F("Vehicle categories the permit covers, as printed.")),
    issuing_authority=(OrganizationSchema | None, F("Organization that issued the permit.")),
)

IDENTITY_SCHEMAS = (
    PassportSchema,
    VisaSchema,
    EVisaSchema,
    ResidencePermitSchema,
    TravelAuthorizationSchema,
    EntryPermitSchema,
    ExitPermitSchema,
    InternationalDrivingPermitSchema,
)
