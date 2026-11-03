"""A traveler on a trip, extending a person with trip-level attributes."""

from __future__ import annotations

from pydantic import field_validator

from schemas.base.base_models import F, SchemaModel
from schemas.base.validators import validate_country_code
from schemas.common.person import PersonSchema


class LoyaltyProgramSchema(SchemaModel):
    """A loyalty or frequent-traveler membership."""

    program_name: str | None = F("Loyalty program name as printed.")
    provider_name: str | None = F("Company that operates the program.")
    member_number: str | None = F("Membership number when it is printed.")
    tier: str | None = F("Membership tier as printed.")


class TravelerSchema(PersonSchema):
    """A person traveling. Nationality and loyalty data are optional."""

    traveler_id: str | None = F("Application identifier for this traveler.")
    nationality: str | None = F("Nationality as printed.")
    nationality_code: str | None = F("ISO country code of nationality when it is known.")
    country_of_residence: str | None = F("Country of residence as printed.")
    loyalty_programs: list[LoyaltyProgramSchema] | None = F("Loyalty memberships printed for this traveler.")
    special_requests: list[str] | None = F("Special requests exactly as printed.")

    @field_validator("nationality_code")
    @classmethod
    def _nationality_code(cls, value: str | None) -> str | None:
        return validate_country_code(value)
