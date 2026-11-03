"""Identification details. Sensitive numbers are optional."""

from __future__ import annotations

from pydantic import field_validator

from schemas.base.base_models import F, SchemaModel
from schemas.base.validators import validate_country_code
from schemas.common.datetime import DateTimeSchema


class IdentificationSchema(SchemaModel):
    """An identity document reference carried inside another record.

    Document numbers, nationality, and dates stay empty when the source does
    not show them. Nothing here is required.
    """

    identification_type: str | None = F("Kind of identification as printed, such as passport or national id.")
    identification_number: str | None = F("Document number when it is present. Leave null when it is unavailable.")
    issuing_country: str | None = F("Issuing country name as printed.")
    issuing_country_code: str | None = F("Issuing country code when it is known.")
    issuing_organization: str | None = F("Authority that issued the identification.")
    nationality: str | None = F("Nationality as printed. Leave null when the document does not state it.")
    issue_date: DateTimeSchema | None = F("Issue date when it is shown.")
    expiry_date: DateTimeSchema | None = F("Expiry date when it is shown.")
    original_number: str | None = F("Document number exactly as printed, including spacing.")

    @field_validator("issuing_country_code")
    @classmethod
    def _issuing_country_code(cls, value: str | None) -> str | None:
        return validate_country_code(value)
