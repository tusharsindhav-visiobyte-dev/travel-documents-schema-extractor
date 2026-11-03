"""Organizations and travel providers."""

from __future__ import annotations

from pydantic import field_validator

from schemas.base.base_models import F, SchemaModel
from schemas.base.enums import ProviderType
from schemas.base.validators import validate_country_code, validate_iata_airline, validate_icao_airline
from schemas.common.contact import ContactSchema
from schemas.common.location import AddressSchema


class OrganizationSchema(SchemaModel):
    """A company, agency, or public authority."""

    organization_id: str | None = F("Application identifier for the organization.")
    name: str | None = F("Common name of the organization.")
    legal_name: str | None = F("Legal name when it differs from the common name.")
    code: str | None = F("Organization code as printed.")
    organization_type: str | None = F("Kind of organization as printed or assigned.")
    contact: ContactSchema | None = F("Contact details for the organization.")
    address: AddressSchema | None = F("Address of the organization.")
    country: str | None = F("Country name as printed.")
    country_code: str | None = F("ISO country code when it is known.")
    original_name: str | None = F("Organization name exactly as printed.")

    @field_validator("country_code")
    @classmethod
    def _country_code(cls, value: str | None) -> str | None:
        return validate_country_code(value)


class ProviderSchema(OrganizationSchema):
    """A provider that sells or operates a travel service."""

    provider_type: ProviderType | None = F("Standardized provider type. Leave null when it is unclear.")
    iata_code: str | None = F("IATA airline or provider code when this provider has one.")
    icao_airline_code: str | None = F("ICAO airline code when it is known.")

    @field_validator("iata_code")
    @classmethod
    def _iata_code(cls, value: str | None) -> str | None:
        return validate_iata_airline(value)

    @field_validator("icao_airline_code")
    @classmethod
    def _icao_code(cls, value: str | None) -> str | None:
        return validate_icao_airline(value)
