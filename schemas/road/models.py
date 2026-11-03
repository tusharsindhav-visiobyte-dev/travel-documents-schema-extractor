"""Car rental, taxi, chauffeur, permit, and parking documents."""

from __future__ import annotations

from pydantic import Field

from schemas.base.base_document import BaseDocumentSchema, declare_document_schema
from schemas.base.base_models import F, SchemaModel
from schemas.base.enums import BookingStatus
from schemas.common.booking import BookingSchema
from schemas.common.datetime import DateTimeSchema
from schemas.common.insurance import InsuranceSchema
from schemas.common.location import LocationSchema
from schemas.common.passenger import PassengerSchema
from schemas.common.payment import CurrencySchema, PaymentSchema
from schemas.common.person import PersonSchema
from schemas.common.provider import OrganizationSchema, ProviderSchema
from schemas.common.transport import VehicleSchema
from schemas.common.traveler import TravelerSchema


class DriverSchema(TravelerSchema):
    """A driver named on a rental or permit. License details stay optional."""

    license_number: str | None = F("Driving license number when the document prints it.")
    license_issuing_country: str | None = F("Country that issued the license, as printed.")
    license_expiry: DateTimeSchema | None = F("License expiry when it is shown.")
    is_primary_driver: bool | None = F("True when the document marks this person as the primary driver.")


class CarRentalDocumentSchema(BaseDocumentSchema):
    """A car rental quote, confirmation, or signed agreement."""

    rental_company: ProviderSchema | None = F("Company providing the vehicle.")
    vehicle: VehicleSchema | None = F("Vehicle reserved or handed over.")
    pickup_location: LocationSchema | None = F("Where the vehicle is picked up.")
    return_location: LocationSchema | None = F("Where the vehicle is returned. It may differ from pickup.")
    pickup: DateTimeSchema | None = F("Pickup date and time, with its own timezone.")
    return_datetime: DateTimeSchema | None = F("Return date and time, with its own timezone.")
    drivers: list[DriverSchema] | None = F("Drivers named on the rental.")
    rental_duration_original: str | None = F("Rental duration exactly as printed.")
    rental_duration_days: int | None = Field(
        default=None,
        ge=0,
        description="Duration in days only when the document states a day count.",
    )
    rental_duration_hours: int | None = Field(
        default=None,
        ge=0,
        description="Duration in hours only when the document states an hour count.",
    )
    insurance_coverage: InsuranceSchema | None = F("Insurance or waiver coverage included or sold with the rental.")
    payment: PaymentSchema | None = F("Payment information.")
    booking: BookingSchema | None = F("Booking reference.")
    booking_status: BookingStatus | None = F("Rental booking status.")
    mileage_policy: str | None = F("Mileage policy exactly as printed.")
    fuel_policy: str | None = F("Fuel policy exactly as printed.")
    remarks: str | None = F("Other rental remarks.")


class HiredVehicleDocumentSchema(BaseDocumentSchema):
    """A taxi or chauffeur booking."""

    provider: ProviderSchema | None = F("Company or driver service providing the ride.")
    pickup_location: LocationSchema | None = F("Pickup place.")
    dropoff_location: LocationSchema | None = F("Drop-off place.")
    pickup: DateTimeSchema | None = F("Pickup date and time.")
    dropoff: DateTimeSchema | None = F("Drop-off date and time when one is stated.")
    passengers: list[PassengerSchema] | None = F("Passengers.")
    vehicle: VehicleSchema | None = F("Vehicle when it is described.")
    driver: PersonSchema | None = F("Driver when the document names one.")
    booking: BookingSchema | None = F("Booking reference.")
    booking_status: BookingStatus | None = F("Booking status.")
    payment: PaymentSchema | None = F("Payment information.")
    fare: CurrencySchema | None = F("Fare when an amount is stated.")
    remarks: str | None = F("Ride remarks.")


class VehiclePermitDocumentSchema(BaseDocumentSchema):
    """Permission to use or drive a vehicle."""

    permit_number: str | None = F("Permit number when it is printed.")
    issuing_authority: OrganizationSchema | None = F("Authority that issued the permit.")
    vehicle: VehicleSchema | None = F("Vehicle covered by the permit.")
    holder: PersonSchema | None = F("Person the permit is issued to.")
    valid_from: DateTimeSchema | None = F("When the permit becomes valid.")
    valid_until: DateTimeSchema | None = F("When the permit stops being valid.")
    permitted_zones: list[str] | None = F("Zones or regions where the permit applies.")
    remarks: str | None = F("Permit remarks.")


class ParkingReservationDocumentSchema(BaseDocumentSchema):
    """A reserved parking space."""

    facility: LocationSchema | None = F("Parking facility.")
    vehicle: VehicleSchema | None = F("Vehicle the reservation is for.")
    start: DateTimeSchema | None = F("When the reservation starts.")
    end: DateTimeSchema | None = F("When the reservation ends.")
    bay: str | None = F("Bay or space identifier as printed.")
    level: str | None = F("Level or floor as printed.")
    booking: BookingSchema | None = F("Booking reference.")
    booking_status: BookingStatus | None = F("Reservation status.")
    payment: PaymentSchema | None = F("Payment information.")
    remarks: str | None = F("Parking remarks.")


_MODULE = __name__


def _doc(name, document_type, base, description, **fields):
    return declare_document_schema(
        name,
        document_type=document_type,
        base=base,
        description=description,
        module=_MODULE,
        category="road",
        fields=fields or None,
    )


CarRentalSchema = _doc(
    "CarRentalSchema",
    "car_rental",
    CarRentalDocumentSchema,
    "A car rental reservation or quote. A signed agreement and a confirmation are separate documents.",
    rate=(CurrencySchema | None, F("Quoted rental rate when one is stated.")),
)

CarRentalConfirmationSchema = _doc(
    "CarRentalConfirmationSchema",
    "car_rental_confirmation",
    CarRentalDocumentSchema,
    "Confirmation that a car rental has been accepted.",
    confirmation_number=(str | None, F("Confirmation number as printed.")),
)

CarRentalAgreementSchema = _doc(
    "CarRentalAgreementSchema",
    "car_rental_agreement",
    CarRentalDocumentSchema,
    "The rental agreement presented or signed at pickup. It is not only a booking confirmation.",
    agreement_number=(str | None, F("Agreement number as printed.")),
    terms_original=(str | None, F("Agreement terms exactly as printed.")),
    signed_at=(DateTimeSchema | None, F("When the agreement was signed, when that time is shown.")),
)

TaxiBookingSchema = _doc(
    "TaxiBookingSchema",
    "taxi_booking",
    HiredVehicleDocumentSchema,
    "A booked taxi ride.",
    taxi_number=(str | None, F("Taxi or medallion number as printed.")),
    meter_fare_original=(str | None, F("Meter fare text exactly as printed.")),
)

ChauffeurBookingSchema = _doc(
    "ChauffeurBookingSchema",
    "chauffeur_booking",
    HiredVehicleDocumentSchema,
    "A chauffeur service booking, which may cover several hours or stops.",
    service_hours=(str | None, F("Hired duration exactly as printed.")),
    stops=(list[LocationSchema] | None, F("Stops between pickup and the final drop-off.")),
    itinerary_notes=(str | None, F("Itinerary notes printed for the chauffeur.")),
)

VehiclePermitSchema = _doc(
    "VehiclePermitSchema",
    "vehicle_permit",
    VehiclePermitDocumentSchema,
    "A permit to drive or operate a vehicle in a stated area or period.",
)

ParkingReservationSchema = _doc(
    "ParkingReservationSchema",
    "parking_reservation",
    ParkingReservationDocumentSchema,
    "A reservation for a parking bay or facility.",
)

ROAD_SCHEMAS = (
    CarRentalSchema,
    CarRentalConfirmationSchema,
    CarRentalAgreementSchema,
    TaxiBookingSchema,
    ChauffeurBookingSchema,
    VehiclePermitSchema,
    ParkingReservationSchema,
)
