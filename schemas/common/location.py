"""Postal addresses, places, and transport terminals."""

from __future__ import annotations

from pydantic import Field, field_validator

from schemas.base.base_models import F, SchemaModel
from schemas.base.validators import validate_country_code, validate_iata_airport, validate_icao_airport
from schemas.common.datetime import TimezoneSchema


class AddressSchema(SchemaModel):
    """A postal address. The printed block is kept even when the parts are incomplete."""

    address_lines: list[str] | None = F("Address lines in the order printed.")
    street: str | None = F("Street name and number when they are separately known.")
    locality: str | None = F("Neighborhood or locality when stated.")
    city: str | None = F("City or town.")
    district: str | None = F("District or county when stated.")
    state: str | None = F("State, province, or region.")
    postal_code: str | None = F("Postal code as printed.")
    country: str | None = F("Country name as printed.")
    country_code: str | None = F("ISO 3166-1 alpha-2 country code when it is known.")
    original_address: str | None = F("Full address block exactly as printed.")

    @field_validator("country_code")
    @classmethod
    def _country_code(cls, value: str | None) -> str | None:
        return validate_country_code(value)


class GeoPointSchema(SchemaModel):
    """Coordinates only when a document or upstream source explicitly provides them."""

    latitude: float | None = Field(default=None, ge=-90, le=90, description="Latitude in decimal degrees.")
    longitude: float | None = Field(default=None, ge=-180, le=180, description="Longitude in decimal degrees.")
    original_text: str | None = F("Coordinate text exactly as printed.")


class LocationSchema(SchemaModel):
    """A named place used as an origin, destination, venue, or stop."""

    location_id: str | None = F("Application identifier for this place.")
    name: str | None = F("Place name.")
    location_type: str | None = F("Kind of place, such as city, airport, hotel, or port.")
    code: str | None = F("Provider or public code for the place, preserved as printed.")
    address: AddressSchema | None = F("Postal address of the place.")
    coordinates: GeoPointSchema | None = F("Coordinates when they are explicitly known.")
    timezone: TimezoneSchema | None = F("Timezone of the place. It is not copied onto other places.")
    city: str | None = F("City name when it is distinct from the place name.")
    country: str | None = F("Country name as printed.")
    country_code: str | None = F("ISO 3166-1 alpha-2 country code when it is known.")
    original_name: str | None = F("Place name exactly as printed.")

    @field_validator("country_code")
    @classmethod
    def _country_code(cls, value: str | None) -> str | None:
        return validate_country_code(value)


class AirportSchema(LocationSchema):
    """An airport. Codes are optional because some documents only print a city name."""

    iata_code: str | None = F("IATA airport code when it is printed or otherwise known.")
    icao_code: str | None = F("ICAO airport code when it is known.")
    terminal: str | None = F("Terminal as printed.")
    city_iata_code: str | None = F("IATA city code when it is distinct from the airport code.")

    @field_validator("iata_code", "city_iata_code")
    @classmethod
    def _iata(cls, value: str | None) -> str | None:
        return validate_iata_airport(value)

    @field_validator("icao_code")
    @classmethod
    def _icao(cls, value: str | None) -> str | None:
        return validate_icao_airport(value)


class RailwayStationSchema(LocationSchema):
    """A railway station. Platform is optional because many tickets omit it."""

    station_code: str | None = F("Station code as printed.")
    station_name: str | None = F("Station name as printed.")
    platform: str | None = F("Platform as printed. Leave null when the document has no platform.")


class BusStationSchema(LocationSchema):
    """A bus station, stop, or terminal."""

    station_code: str | None = F("Stop or station code as printed.")
    station_name: str | None = F("Stop or station name as printed.")
    bay: str | None = F("Bay or stand as printed.")
