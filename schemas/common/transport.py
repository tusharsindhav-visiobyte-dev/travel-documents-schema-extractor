"""Reusable transport, route, vehicle, and seat records."""

from __future__ import annotations

from pydantic import Field

from schemas.base.base_models import F, SchemaModel
from schemas.base.enums import BookingStatus, CabinClass, TransportMode
from schemas.common.baggage import BaggageAllowanceSchema
from schemas.common.datetime import DateTimeSchema
from schemas.common.location import LocationSchema
from schemas.common.passenger import PassengerSchema
from schemas.common.provider import ProviderSchema


class VehicleSchema(SchemaModel):
    """A road or rental vehicle. Registration is optional."""

    vehicle_category: str | None = F("Vehicle category as printed, such as compact or SUV.")
    make: str | None = F("Vehicle make.")
    model: str | None = F("Vehicle model.")
    year: int | None = Field(default=None, ge=1800, le=2200, description="Model year when it is printed.")
    color: str | None = F("Color as printed.")
    registration_number: str | None = F("Registration or license plate as printed.")
    vin: str | None = F("Vehicle identification number when the document prints it.")
    fuel_type: str | None = F("Fuel type as printed.")
    transmission: str | None = F("Transmission as printed.")
    passenger_capacity: int | None = Field(
        default=None,
        ge=0,
        description="Passenger capacity when the document states it.",
    )
    original_description: str | None = F("Vehicle description exactly as printed.")


class RouteSchema(SchemaModel):
    """A path from an origin to a destination, with optional intermediate stops."""

    route_id: str | None = F("Route identifier as printed or assigned.")
    origin: LocationSchema | None = F("Where the route starts.")
    destination: LocationSchema | None = F("Where the route ends.")
    stops: list[LocationSchema] | None = F("Intermediate stops in journey order.")
    distance_original: str | None = F("Distance exactly as printed, including the unit.")
    distance_km: float | None = Field(
        default=None,
        ge=0,
        description="Distance in kilometres only when the unit is known to be kilometres.",
    )


class SeatAssignmentSchema(SchemaModel):
    """A seat or berth linked to one passenger and one segment."""

    passenger_ref: str | None = F("Reference to the passenger, such as a traveler id or list index.")
    segment_ref: str | None = F("Reference to the segment this seat belongs to.")
    seat: str | None = F("Seat, berth, or space identifier as printed.")
    coach: str | None = F("Coach, carriage, or cabin as printed.")
    cabin_class: CabinClass | None = F("Cabin class for this assignment when it is known.")
    travel_class: str | None = F("Class of travel as printed.")
    baggage_allowance: BaggageAllowanceSchema | None = F("Baggage allowance that applies to this assignment.")
    original_text: str | None = F("Seat assignment text exactly as printed.")


class TransportSchema(SchemaModel):
    """A generic journey leg used inside itineraries and mixed documents."""

    transport_id: str | None = F("Identifier for this leg.")
    mode: TransportMode | None = F("Standardized transport mode. Leave null when it is unclear.")
    mode_original: str | None = F("Transport mode exactly as printed.")
    carrier: ProviderSchema | None = F("Carrier or operator.")
    service_number: str | None = F("Flight, train, bus, or other service number as printed.")
    route: RouteSchema | None = F("Origin, destination, and stops.")
    departure: DateTimeSchema | None = F("Departure date and time. Its timezone is independent of arrival.")
    arrival: DateTimeSchema | None = F("Arrival date and time. Its timezone is independent of departure.")
    departure_location: LocationSchema | None = F("Where this leg starts.")
    arrival_location: LocationSchema | None = F("Where this leg ends.")
    seat: str | None = F("Seat when the leg has a single printed seat.")
    vehicle: VehicleSchema | None = F("Vehicle used for this leg.")
    booking_status: BookingStatus | None = F("Status of this leg.")
    overnight_journey: bool | None = F("True when the document or the known dates show an overnight journey.")
    international: bool | None = F("True or false only when it is established. It is not inferred from missing countries.")
    passengers: list[PassengerSchema] | None = F("Passengers on this leg.")
